# sampleAgents.py
# parsons/07-oct-2017
#
# Version 1.1
#
# Some simple agents to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agents here are extensions written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import util

class HungrySurvivalCornerSeekingAgent(Agent):

    def __init__(self):
        self.lastMove = Directions.STOP
        self.visitedCorners = []
        self.position = (0, 0)
        self.scared = True
        self.walls = []
        self.legalMoves = []
        self.offsetMapping = {
            Directions.WEST: (-1, 0),
            Directions.NORTH: (0, 1),
            Directions.EAST: (1, 0),
            Directions.SOUTH: (0, -1)
        }

    def sortCoordsByDistance(self, coordList, distList):
        gap = len(distList) / 2
        while gap > 0:
            for i in range(gap, len(distList)):
                tempCoord = coordList[i]
                tempDist = distList[i]
                j = i
                while j >= gap and distList[j - gap] > tempDist:
                    coordList[j] = coordList[j - gap]
                    distList[j] = distList[j - gap]
                    j = j - gap
                    coordList[j] = tempCoord
                distList[j] = tempDist
            gap = gap / 2

    def distanceWithWalls(self, tupleA, tupleB):
        return util.manhattanDistance(tupleA, tupleB)

    def pathFinder(self, tupleA, tupleB, distance):
        return -1

    def getAction(self, state):
        self.legalMoves = api.legalActions(state)
        if Directions.STOP in self.legalMoves:
            self.legalMoves.remove(Directions.STOP)

        self.position = api.whereAmI(state)
        self.walls = api.walls(state)
        ghostLocations = api.ghostsDistanceLimited(state)
        ghostDistances = []

        foodLocations = api.foodDistanceLimited(state)
        capsuleLocations = api.capsulesDistanceLimited(state)
        foodDistances = []

        cornersToVisit = api.corners(state)
        for corner in self.visitedCorners:
            cornersToVisit.remove(corner)

        for ghost in ghostLocations:
            ghostDistances.append(self.distanceWithWalls(self.position, ghost))

        for capsule in capsuleLocations:
            foodLocations.append(capsule)

        for location in foodLocations:
            foodDistances.append(self.distanceWithWalls(location, self.position))

        self.sortCoordsByDistance(foodLocations, foodDistances)

        if len(ghostLocations) > 0:
            bestMove = random.choice(self.legalMoves)
            if len(ghostLocations) > 1:
                closestGhost = ghostLocations[0] if ghostDistances[0] < ghostDistances[1] else ghostLocations[1]
            else:
                closestGhost = ghostLocations[0]
            ghostStates = state.getGhostStates()
            for i in range(len(ghostStates)):
                if ghostStates[i].getPosition() == closestGhost and ghostStates[i].scaredTimer > 0:
                    self.scared = False
                    break
                else:
                    self.scared = True
            for move in self.legalMoves:
                nextSpot = tuple(map(sum, zip(self.offsetMapping[move], self.position)))
                distanceToGhost = self.distanceWithWalls(closestGhost, nextSpot)
                currentDistanceToGhost = self.distanceWithWalls(closestGhost, self.position)
                if distanceToGhost > currentDistanceToGhost and self.scared:
                    bestMove = move
                if distanceToGhost < currentDistanceToGhost and not self.scared:
                    bestMove = move
            return api.makeMove(bestMove, self.legalMoves)
        elif len(foodLocations) > 0:
            closestFood = foodLocations[0]
            closestFoodDistance = self.distanceWithWalls(self.position, closestFood)
            if len(foodLocations) > 2 and (closestFoodDistance == self.distanceWithWalls(self.position, foodLocations[1])):
                closestFood = foodLocations[random.randint(0, 1)]
            if len(capsuleLocations) > 0 and (closestFoodDistance == self.distanceWithWalls(self.position, capsuleLocations[0])):
                closestFood = capsuleLocations[0]
            validMoves = []
            if closestFood[0] < self.position[0] and Directions.WEST in self.legalMoves:
                validMoves.append(Directions.WEST)
            if closestFood[0] > self.position[0] and Directions.EAST in self.legalMoves:
                validMoves.append(Directions.EAST)
            if closestFood[1] < self.position[1] and Directions.SOUTH in self.legalMoves:
                validMoves.append(Directions.SOUTH)
            if closestFood[1] > self.position[1] and Directions.NORTH in self.legalMoves:
                validMoves.append(Directions.NORTH)
            if len(validMoves) == 0 and not self.lastMove == Directions.STOP and self.lastMove in self.legalMoves:
                return api.makeMove(self.lastMove, self.legalMoves)
            self.lastMove = random.choice(validMoves if len(validMoves) > 0 else self.legalMoves)
        elif len(cornersToVisit) > 0:
            nextCorner = cornersToVisit[0]
        self.lastMove = self.lastMove if self.lastMove in self.legalMoves else random.choice(self.legalMoves)
        return api.makeMove(self.lastMove, self.legalMoves)


class SurvivalAgent(Agent):

    def getAction(self, state):
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        pacmanPosition = api.whereAmI(state)
        ghostLocations = api.ghostsDistanceLimited(state)
        ghostDistances = []

        for ghost in ghostLocations:
            ghostDistances.append(util.manhattanDistance(pacmanPosition, ghost))

        offsetMapping = {
            Directions.WEST: (-1, 0),
            Directions.NORTH: (0, 1),
            Directions.EAST: (1, 0),
            Directions.SOUTH: (0, -1)
        }
        bestMove = random.choice(legal)
        if len(ghostLocations) > 0:
            if len(ghostLocations) > 1:
                closestGhost = ghostLocations[0] if ghostDistances[0] < ghostDistances[1] else ghostLocations[1]
            else:
                closestGhost = ghostLocations[0]
            for move in legal:
                nextSpot = tuple(map(sum, zip(offsetMapping[move], pacmanPosition)))
                distanceToGhost = util.manhattanDistance(closestGhost, nextSpot)
                currentDistanceToGhost = util.manhattanDistance(closestGhost, pacmanPosition)
                if distanceToGhost > currentDistanceToGhost:
                    bestMove = move
        return api.makeMove(bestMove, legal)

class HungryAgent(Agent):

    def sortFoodByDistance(self, foodList, distList):
        gap = len(distList) / 2
        while gap > 0:
            for i in range(gap, len(distList)):
                tempFood = foodList[i]
                tempDist = distList[i]
                j = i
                while j >= gap and distList[j - gap] > tempDist:
                    foodList[j] = foodList[j - gap]
                    distList[j] = distList[j - gap]
                    j = j - gap
                    foodList[j] = tempFood
                distList[j] = tempDist
            gap = gap / 2

    def getAction(self, state):
        legal = api.legalActions(state)
        pacmanPosition = api.whereAmI(state)
        foodLocations = api.foodDistanceLimited(state)
        capsuleLocations = api.capsulesDistanceLimited(state)
        foodDistances = []

        for capsule in capsuleLocations:
            foodLocations.append(capsule)

        for location in foodLocations:
            foodDistances.append(util.manhattanDistance(location, pacmanPosition))

        self.sortFoodByDistance(foodLocations, foodDistances)

        if len(foodLocations) > 0:
            closestFood = foodLocations[0]
            if len(foodLocations) > 2 and (util.manhattanDistance(pacmanPosition, closestFood) == util.manhattanDistance(pacmanPosition, foodLocations[1])):
                closestFood = foodLocations[random.randint(0, 1)]
            if len(capsuleLocations) > 0 and (util.manhattanDistance(pacmanPosition, closestFood) == util.manhattanDistance(pacmanPosition, capsuleLocations[0])):
                closestFood = capsuleLocations[0]
            validMoves = []
            if closestFood[0] < pacmanPosition[0] and Directions.WEST in legal:
                validMoves.append(Directions.WEST)
            if closestFood[0] > pacmanPosition[0] and Directions.EAST in legal:
                validMoves.append(Directions.EAST)
            if closestFood[1] < pacmanPosition[1] and Directions.SOUTH in legal:
                validMoves.append(Directions.SOUTH)
            if closestFood[1] > pacmanPosition[1] and Directions.NORTH in legal:
                validMoves.append(Directions.NORTH)
            return api.makeMove(random.choice(validMoves), legal)
        return api.makeMove(random.choice(legal), legal)

class LeftTurnAgent(Agent):
    "An agent that turns left at every opportunity"

    def getAction(self, state):
        legal = state.getLegalPacmanActions()
        current = state.getPacmanState().configuration.direction
        if current == Directions.STOP: current = Directions.NORTH
        left = Directions.LEFT[current]
        if left in legal: return left
        if current in legal: return current
        if Directions.RIGHT[current] in legal: return Directions.RIGHT[current]
        if Directions.LEFT[left] in legal: return Directions.LEFT[left]
        return Directions.STOP

# RandomAgent
#
# A very simple agent. Just makes a random pick every time that it is
# asked for an action.
class RandomAgent(Agent):

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)

# RandomishAgent
#
# A tiny bit more sophisticated. Having picked a direction, keep going
# until that direction is no longer possible. Then make a random
# choice.
class RandomishAgent(Agent):

    # Constructor
    #
    # Create a variable to hold the last action
    def __init__(self):
         self.last = Directions.STOP
    
    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # If we can repeat the last action, do it. Otherwise make a
        # random choice.
        if self.last in legal:
            return api.makeMove(self.last, legal)
        else:
            pick = random.choice(legal)
            # Since we changed action, record what we did
            self.last = pick
            return api.makeMove(pick, legal)

# SensingAgent
#
# Doesn't move, but reports sensory data available to Pacman
class SensingAgent(Agent):

    def getAction(self, state):

        # Demonstrates the information that Pacman can access about the state
        # of the game.

        # What are the current moves available
        legal = api.legalActions(state)
        print "Legal moves: ", legal

        # Where is Pacman?
        pacman = api.whereAmI(state)
        print "Pacman position: ", pacman

        # Where are the ghosts?
        print "Ghost positions:"
        # theGhosts = api.ghostsDistanceLimited(state)
        theGhosts = api.ghosts(state)
        for i in range(len(theGhosts)):
            print theGhosts[i]

        # How far away are the ghosts?
        print "Distance to ghosts:"
        for i in range(len(theGhosts)):
            print util.manhattanDistance(pacman,theGhosts[i])

        # Where are the capsules?
        print "Capsule locations:"
        # print api.capsulesDistanceLimited(state)
        print api.capsules(state)
        
        # Where is the food?
        print "Food locations: "
        # print api.foodDistanceLimited(state)
        print api.food(state)

        # Where are the walls?
        print "Wall locations: "
        print api.walls(state)
        
        # getAction has to return a move. Here we pass "STOP" to the
        # API to ask Pacman to stay where they are.
        return api.makeMove(Directions.STOP, legal)
