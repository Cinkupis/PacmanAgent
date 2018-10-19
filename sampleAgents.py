from pacman import Directions
from game import Agent
import api
import random
import util
import math

class PartialAgent(Agent):

    SCARED = 'SCARED'
    HUNGRY = 'HUNGRY'
    SEARCH = 'SEARCH'

    def __init__(self):
        self.visitedWaypoints = []
        self.doOnce = True
        self.lastDirection = Directions.STOP
        self.lastBadDirection = Directions.STOP
        self.lastSpot = None
        self.position = None
        self.walls = []
        self.legalDirections = []
        self.knownGhosts = []
        self.knownWaypoints = []
        self.knownFood = []
        self.knownCapsules = []
        self.offsetDirectionalMapping = {
            Directions.WEST: (-1, 0),
            Directions.NORTH: (0, 1),
            Directions.EAST: (1, 0),
            Directions.SOUTH: (0, -1)
        }
        self.oppositeOf = {
            Directions.WEST: Directions.EAST,
            Directions.NORTH: Directions.SOUTH,
            Directions.EAST: Directions.WEST,
            Directions.SOUTH: Directions.NORTH
        }

    def renewInformation(self, state):
        self.position = api.whereAmI(state)

        self.legalDirections = api.legalActions(state)
        if Directions.STOP in self.legalDirections:
            self.legalDirections.remove(Directions.STOP)

        self.knownGhosts = api.ghosts(state)
        self.knownFood = api.food(state)
        self.knownCapsules = api.capsules(state)

        for waypoint in self.knownWaypoints:
            if self.getManhattanDist(self.position, waypoint) == 0 and waypoint not in self.visitedWaypoints:
                self.visitedWaypoints.append(waypoint)
                self.knownWaypoints.remove(waypoint)

        foodDistances = []
        for food in self.knownFood:
            foodDistances.append(self.getManhattanDist(self.position, food))
        self.sortCoordsByDistance(self.knownFood, foodDistances)

    def instantiateNormalizeOnce(self, state):
        self.position = api.whereAmI(state)
        self.walls = api.walls(state)
        self.legalDirections = api.legalActions(state)
        self.knownGhosts = api.ghosts(state)
        self.knownWaypoints = api.corners(state)
        self.knownFood = api.food(state)
        self.knownCapsules = api.capsules(state)
        for i in range(len(self.knownWaypoints)):
            if self.knownWaypoints[i][0] == 0:
                self.knownWaypoints[i] = (self.knownWaypoints[i][0] + 1, self.knownWaypoints[i][1])
            else:
                self.knownWaypoints[i] = (self.knownWaypoints[i][0] - 1, self.knownWaypoints[i][1])
            if self.knownWaypoints[i][1] == 0:
                self.knownWaypoints[i] = (self.knownWaypoints[i][0], self.knownWaypoints[i][1] + 1)
            else:
                self.knownWaypoints[i] = (self.knownWaypoints[i][0], self.knownWaypoints[i][1] - 1)
        self.doOnce = False

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

    def getManhattanDist(self, objectA, objectB):
        return util.manhattanDistance(objectA, objectB)

    def getDiagonalDist(self, objectA, objectB):
        return math.sqrt((objectA[0] - objectB[0]) ** 2 + (objectA[1] - objectB[1]) ** 2)

    def wallInBetweenPacman(self, object):
        if self.getManhattanDist(object, self.position) == 2:
            spotDifference = (object[0] - self.position[0], object[1] - self.position[1])
            if spotDifference[0] == 0 or spotDifference[1] == 0:
                spotInBetween = tuple(map(sum, zip(self.position, spotDifference)))
                if spotInBetween in self.walls:
                    return True
        return False

    def filterGreedyDirections(self, greedyDirections):
        if len(greedyDirections) > 0:
            for direction in greedyDirections:
                if direction not in self.legalDirections:
                    greedyDirections.remove(direction)
        return greedyDirections

    def getGreedyDirections(self, goalCoord, fromCoord):
        greedyDirections = []
        if goalCoord[0] < fromCoord[0] and Directions.WEST in self.legalDirections:
            greedyDirections.append(Directions.WEST)
        if goalCoord[0] > fromCoord[0] and Directions.EAST in self.legalDirections:
            greedyDirections.append(Directions.EAST)
        if goalCoord[1] < fromCoord[1] and Directions.SOUTH in self.legalDirections:
            greedyDirections.append(Directions.SOUTH)
        if goalCoord[1] > fromCoord[1] and Directions.NORTH in self.legalDirections:
            greedyDirections.append(Directions.NORTH)
        return greedyDirections

    def evaluateScaryConditions(self):
        conditions = []
        if len(self.knownGhosts) > 0:
            ghostDistances = []
            for ghost in self.knownGhosts:
                ghostDistances.append(self.getManhattanDist(self.position, ghost))
            if len(self.knownGhosts) > 1:
                closestGhost = self.knownGhosts[0] if ghostDistances[0] < ghostDistances[1] else self.knownGhosts[1]
            else:
                closestGhost = self.knownGhosts[0]
            if not self.wallInBetweenPacman(closestGhost):
                conditions.append(self.SCARED)
                conditions.append(closestGhost)
                if len(self.knownFood) > 0:
                    conditions.append(self.knownFood[-1])
        return conditions

    def evaluateHungryConditions(self):
        conditions = []
        if len(self.knownFood) > 0:
            for i in range(len(self.knownFood)):
                if not self.wallInBetweenPacman(self.knownFood[0]):
                    conditions.append(self.HUNGRY)
                    conditions.append(self.knownFood[i])
                    if len(self.knownFood) > 1:
                        conditions.append(self.knownFood[-1])
                    break
        return conditions

    def evaluateSearchConditions(self):
        conditions = []
        waypointDistances = []
        if len(self.knownWaypoints) > 0:
            for waypoint in self.knownWaypoints:
                waypointDistances.append(self.getManhattanDist(self.position, waypoint))
            self.sortCoordsByDistance(self.knownWaypoints, waypointDistances)
            conditions.append(self.SEARCH)
            conditions.append(self.knownWaypoints[0])
        return conditions

    def runAway(self, runFrom):
        previousDistance = 0
        bestDirection = Directions.STOP
        for direction in self.legalDirections:
            nextSpot = tuple(map(sum, zip(self.offsetDirectionalMapping[direction], self.position)))
            nextSpotDistanceToGhost = self.getDiagonalDist(nextSpot, runFrom)
            currentDistanceToGhost = self.getManhattanDist(self.position, runFrom)
            if nextSpotDistanceToGhost >= currentDistanceToGhost and nextSpotDistanceToGhost >= previousDistance:
                bestDirection = direction
                previousDistance = nextSpotDistanceToGhost
        self.lastSpot = self.position
        self.lastDirection = bestDirection
        return bestDirection

    def runTowards(self, runTo):
        bestDirection = Directions.STOP
        greedyDirections = self.filterGreedyDirections(self.getGreedyDirections(runTo, self.position))
        previousDistance = self.getManhattanDist(self.position, runTo)
        if len(greedyDirections) == 0:
            for direction in self.legalDirections:
                nextSpot = tuple(map(sum, zip(self.offsetDirectionalMapping[direction], self.position)))
                nextSpotDistanceToObject = self.getDiagonalDist(nextSpot, runTo)
                currentDistanceToObject = self.getManhattanDist(self.position, runTo)
                if nextSpotDistanceToObject <= currentDistanceToObject and nextSpotDistanceToObject <= previousDistance:
                    bestDirection = direction
                    previousDistance = nextSpotDistanceToObject
        else:
            for direction in greedyDirections:
                nextSpot = tuple(map(sum, zip(self.offsetDirectionalMapping[direction], self.position)))
                nextSpotDistanceToObject = self.getDiagonalDist(nextSpot, runTo)
                currentDistanceToObject = self.getManhattanDist(self.position, runTo)
                if nextSpotDistanceToObject <= currentDistanceToObject and nextSpotDistanceToObject <= previousDistance:
                    bestDirection = direction
                    previousDistance = nextSpotDistanceToObject

        if self.lastDirection != Directions.STOP and bestDirection == self.oppositeOf[self.lastDirection]:
            if len(self.legalDirections) > 1:
                self.legalDirections.remove(self.oppositeOf[self.lastDirection])
            bestDirection = random.choice(self.legalDirections)
        elif bestDirection == Directions.STOP:
            bestDirection = self.lastDirection if self.lastDirection in self.legalDirections else random.choice(self.legalDirections)
        self.lastDirection = bestDirection
        self.lastSpot = self.position
        return bestDirection

    def getAction(self, state):
        if self.doOnce:
            self.instantiateNormalizeOnce(state)

        self.renewInformation(state)

        environmentConditions = self.evaluateScaryConditions()
        if len(environmentConditions) > 0:
            bestDirection = self.runAway(environmentConditions[1])
            if len(environmentConditions) == 3:
                if environmentConditions[2] not in self.knownWaypoints:
                    self.knownWaypoints.append(environmentConditions[2])
            return api.makeMove(bestDirection, self.legalDirections)

        environmentConditions = self.evaluateHungryConditions()
        if len(environmentConditions) > 0:
            bestDirection = self.runTowards(environmentConditions[1])
            if environmentConditions[1] not in self.knownWaypoints:
                self.knownWaypoints.append(environmentConditions[1])
            if len(environmentConditions) == 3:
                if environmentConditions[2] not in self.knownWaypoints:
                    self.knownWaypoints.append(environmentConditions[2])
            return api.makeMove(bestDirection, self.legalDirections)

        environmentConditions = self.evaluateSearchConditions()
        if len(environmentConditions) > 0:
            bestDirection = self.runTowards(environmentConditions[1])
            return api.makeMove(bestDirection, self.legalDirections)

        self.lastDirection = self.lastDirection if self.lastDirection in self.legalDirections else random.choice(self.legalDirections)
        self.lastSpot = self.position
        return api.makeMove(self.lastDirection, self.legalDirections)

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

class SensingAgent(Agent):

    def getAction(self, state):

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
