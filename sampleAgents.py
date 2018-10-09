from pacman import Directions
from game import Agent
import api
import random
import util

class HungrySurvivalCornerSeekingAgent(Agent):

    def __init__(self):
        self.lastDirection = Directions.STOP
        self.lastSpot = (0, 0)
        self.visitedCorners = []
        self.position = (0, 0)
        self.scared = True
        self.walls = []
        self.legalDirections = []
        self.offsetDirectionalMapping = {
            Directions.WEST: (-1, 0),
            Directions.NORTH: (0, 1),
            Directions.EAST: (1, 0),
            Directions.SOUTH: (0, -1)
        }

        self.pathTraversal = []

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

    def getDistanceWithWalls(self, tupleA, tupleB):
        return util.manhattanDistance(tupleA, tupleB)
        # return max(self.pathFinder(tupleA, tupleB), util.manhattanDistance(tupleA, tupleB))
        # return max(self.pathFinder(tupleA, tupleB), self.pathFinder(tupleB, tupleA))

    # Recursion limit
    def pathFinder(self, tupleA, tupleB):
        if tupleA == tupleB:
            return len(self.pathTraversal)
        for direction in self.offsetDirectionalMapping:
            possibleSpot = tuple(map(sum, zip(self.offsetDirectionalMapping[direction], tupleA)))
            if possibleSpot not in self.walls and possibleSpot not in self.pathTraversal:
                self.pathTraversal.append(possibleSpot)
                return min(self.pathFinder(possibleSpot, tupleB), self.pathFinder(tupleB, possibleSpot))

        # What to do in case of dead end?
        # How to classify a dead end and filter it out during recursion?

        # if len(self.pathTraversal) < util.manhattanDistance(tupleA, tupleB):
        #     return util.manhattanDistance(tupleA, tupleB)**2
        # else:
        #     return len(self.pathTraversal)

    def getValidDirections(self, goalCoord):
        validDirections = []
        if goalCoord[0] < self.position[0] and Directions.WEST in self.legalDirections:
            validDirections.append(Directions.WEST)
        if goalCoord[0] > self.position[0] and Directions.EAST in self.legalDirections:
            validDirections.append(Directions.EAST)
        if goalCoord[1] < self.position[1] and Directions.SOUTH in self.legalDirections:
            validDirections.append(Directions.SOUTH)
        if goalCoord[1] > self.position[1] and Directions.NORTH in self.legalDirections:
            validDirections.append(Directions.NORTH)
        return validDirections

    def getAction(self, state):
        self.legalDirections = api.legalActions(state)
        if Directions.STOP in self.legalDirections:
            self.legalDirections.remove(Directions.STOP)

        self.position = api.whereAmI(state)
        self.walls = api.walls(state)
        ghostLocations = api.ghostsDistanceLimited(state)
        ghostDistances = []

        foodLocations = api.foodDistanceLimited(state)
        capsuleLocations = api.capsulesDistanceLimited(state)
        foodDistances = []

        cornersToVisit = api.corners(state)
        cornerDistances = []

        if self.position in cornersToVisit and self.position not in self.visitedCorners:
            self.visitedCorners.append(self.position)

        for corner in self.visitedCorners:
            cornersToVisit.remove(corner)

        for ghost in ghostLocations:
            ghostDistances.append(self.getDistanceWithWalls(self.position, ghost))

        for capsule in capsuleLocations:
            foodLocations.append(capsule)

        for location in foodLocations:
            foodDistances.append(self.getDistanceWithWalls(self.position, location))

        for corner in cornersToVisit:
            cornerDistances.append(self.getDistanceWithWalls(self.position, corner))

        self.sortCoordsByDistance(foodLocations, foodDistances)
        self.sortCoordsByDistance(cornersToVisit, cornerDistances)

        if len(ghostLocations) > 0:
            bestDirection = random.choice(self.legalDirections)
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
            for direction in self.legalDirections:
                nextSpot = tuple(map(sum, zip(self.offsetDirectionalMapping[direction], self.position)))
                distanceToGhost = self.getDistanceWithWalls(nextSpot, closestGhost)
                currentDistanceToGhost = self.getDistanceWithWalls(self.position, closestGhost)
                if distanceToGhost > currentDistanceToGhost and self.scared:
                    bestDirection = direction
                if distanceToGhost < currentDistanceToGhost and not self.scared:
                    bestDirection = direction
            self.lastSpot = self.position
            return api.makeMove(bestDirection, self.legalDirections)

        elif len(foodLocations) > 0:
            closestFood = foodLocations[0]
            closestFoodDistance = self.getDistanceWithWalls(self.position, closestFood)
            if len(foodLocations) > 2 and (closestFoodDistance == self.getDistanceWithWalls(self.position, foodLocations[1])):
                closestFood = foodLocations[random.randint(0, 1)]
            if len(capsuleLocations) > 0 and (closestFoodDistance == self.getDistanceWithWalls(self.position, capsuleLocations[0])):
                closestFood = capsuleLocations[0]
            validDirections = self.getValidDirections(closestFood)
            if len(validDirections) == 0 and not self.lastDirection == Directions.STOP and self.lastDirection in self.legalDirections:
                return api.makeMove(self.lastDirection, self.legalDirections)
            self.lastDirection = random.choice(validDirections if len(validDirections) > 0 else self.legalDirections)

        elif len(cornersToVisit) > 0:
            nextCorner = cornersToVisit[0]
            validDirections = self.getValidDirections(nextCorner)
            if len(validDirections) == 0 and not self.lastDirection == Directions.STOP and self.lastDirection in self.legalDirections:
                return api.makeMove(self.lastDirection, self.legalDirections)
            self.lastDirection = random.choice(validDirections if len(validDirections) > 0 else self.legalDirections)

        self.lastDirection = self.lastDirection if self.lastDirection in self.legalDirections else random.choice(self.legalDirections)
        if len(self.legalDirections) > 1 and tuple(map(sum, zip(self.offsetDirectionalMapping[self.lastDirection], self.position))) == self.lastSpot:
            self.legalDirections.remove(self.lastDirection)
            self.lastDirection = random.choice(self.legalDirections)
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
