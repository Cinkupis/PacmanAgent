import math
import operator
import random
import sys

import deterministicApi as api
import nonDeterministicApi
import util
from game import Agent, Directions

class NonDeterministicAgent(Agent):
    def __init__(self):
        """
        Initialization of parameters
        """
        self.doOnce = True
        self.lastDirection = Directions.STOP
        self.lastSpot = None
        self.position = None
        self.walls = None
        self.legalDirections = None
        self.knownGhosts = None
        self.knownWaypoints = []
        self.visitedWaypoints = []
        self.knownFood = None
        self.offsetDirectionalMapping = None
        self.oppositeOf = None
        self.ranFromGhost = False
        self.probabilityForward = 0.8
        self.probabilitySideways = 0.1

    def final(self, state):
        """
        Runs in between games.
        Resets knowledge about the world to the starting point.
        """
        self.doOnce = True
        self.lastDirection = Directions.STOP
        self.lastSpot = None
        self.position = None
        self.walls = None
        self.legalDirections = None
        self.knownGhosts = None
        self.knownWaypoints = []
        self.visitedWaypoints = []
        self.knownFood = None
        self.offsetDirectionalMapping = None
        self.oppositeOf = None
        self.ranFromGhost = False
        self.map = []
        print "Did I win? I hope I did. Of course I did! I am confident in myself!"

    def reEvaluateState(self):
        for y in range(self.walls[-1][1] + 1):
            for x in range(self.walls[-1][0] + 1):
                if (x, y) in self.knownFood:
                    self.map[x][y] = 5
                    continue
                if (x, y) not in self.knownFood and (x, y) not in self.walls:
                    self.map[x][y] = 0
                if (x, y) in self.knownGhosts:
                    self.map[x][y] = -500

        self.runIterationsUntilConverge()

        return self.maximumExpectedUtility()

    def runIterationsUntilConverge(self):
        previousMap = self.map
        start = True
        print "NEXT"
        #while abs(previousMap[self.knownWaypoints[0][0]][self.knownWaypoints[0][1]] - self.map[self.knownWaypoints[0][0]][self.knownWaypoints[0][1]]) >= 0.001 or start:
        for i in range(5):
        #while abs(previousMap[self.position[0]][self.position[1]] - self.map[self.position[0]][self.position[1]]) >= 0.01 or start:
            start = False
            previousMap = self.map
            for y in range(self.walls[-1][1] + 1):
                for x in range(self.walls[-1][0] + 1):
                    maxSpot = (x, y)
                    if maxSpot not in self.knownWaypoints and maxSpot not in self.knownFood and maxSpot not in self.walls and self.map[x][y] != 5:
                        for direction in [Directions.NORTH, Directions.EAST, Directions.SOUTH, Directions.WEST]:
                            nextSpot = tuple(map(sum, zip((x, y), self.offsetDirectionalMapping[direction])))
                            if (nextSpot[0] < len(self.map)) and (nextSpot[1] < len(self.map[0])):
                                utility = self.map[nextSpot[0]][nextSpot[1]] * self.probabilityForward
                                if nextSpot not in self.walls:
                                    sidewaysLeft = tuple(map(sum, zip((x, y), self.offsetDirectionalMapping[Directions.LEFT[direction]])))
                                    if sidewaysLeft not in self.walls and sidewaysLeft[0] < len(self.map) and sidewaysLeft[1] < len(self.map[0]):
                                        utility += self.map[sidewaysLeft[0]][sidewaysLeft[1]] * self.probabilitySideways
                                    else:
                                        utility += self.map[x][y] * self.probabilitySideways
                                    sidewaysRight = tuple(map(sum, zip((x, y), self.offsetDirectionalMapping[Directions.RIGHT[direction]])))
                                    if sidewaysRight not in self.walls and sidewaysRight[0] < len(self.map) and sidewaysRight[1] < len(self.map[0]):
                                        utility += self.map[sidewaysRight[0]][sidewaysRight[1]] * self.probabilitySideways
                                    else:
                                        utility += self.map[x][y] * self.probabilitySideways
                                    self.map[nextSpot[0]][nextSpot[1]] = utility
                                    if self.map[nextSpot[0]][nextSpot[1]] > self.map[maxSpot[0]][maxSpot[1]]:
                                        maxSpot = nextSpot
                        self.map[x][y] = -1 + self.map[maxSpot[0]][maxSpot[1]]
            #if abs(previousMap[self.position[0]][self.position[1]] - self.map[self.position[0]][self.position[1]]) >= 0.01:
            #    break;
            self.printMap()
            print "--------------------------------------------------------------------------------------"

    def printMap(self):
        for y in range(self.walls[-1][1] + 1):
            for x in range(self.walls[-1][0] + 1):
                print self.map[x][y],
                print "|",
            print

    def maximumExpectedUtility(self):
        utilities = {}
        for direction in self.legalDirections:
            nextSpot = tuple(map(sum, zip(self.position, self.offsetDirectionalMapping[direction])))
            utilities[direction] = self.map[nextSpot[0]][nextSpot[1]]
        bestDirection = max(utilities.iteritems(), key=operator.itemgetter(1))[0]
        return bestDirection

    def renewInformation(self, state):
        """
        Run at every tick.
        Pacman updates its' knowledge about the world/environment
        """
        self.position = nonDeterministicApi.whereAmI(state)

        self.legalDirections = nonDeterministicApi.legalActions(state)
        if Directions.STOP in self.legalDirections:
            self.legalDirections.remove(Directions.STOP)

        self.knownGhosts = nonDeterministicApi.ghosts(state)
        self.knownFood = nonDeterministicApi.food(state)

        for waypoint in self.knownWaypoints:
            if self.getManhattanDist(self.position, waypoint) == 0:
                self.knownWaypoints.remove(waypoint)

        if len(self.knownFood) > 0:
            for i in range(len(self.knownFood)):
                if self.knownFood[i] not in self.knownWaypoints:
                    self.knownWaypoints.append(self.knownFood[i])

    def instantiateNormalizeOnce(self, state):
        """
        Runs only once per pacman game.
        Instantiates static information that is true at the time of environment creation and ever since that point.
        Normalizes corner tuples into reachable spots (since api.corners(state) returns corners that are indeed walls.)
        If, for whatever reason, the normalized corner coordinates are inside the array of known wall coordinates (meaning
        maybe there is a double wall around the corner, or layout is not rectangular) then Pacman scraps such corners from
        knownWaypoints array.
        """
        self.walls = nonDeterministicApi.walls(state)
        self.knownWaypoints = nonDeterministicApi.corners(state)
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
        for i in range(len(self.knownWaypoints)):
            if self.knownWaypoints[i][0] == 0:
                self.knownWaypoints[i] = (int(self.knownWaypoints[i][0] + 1), int(self.knownWaypoints[i][1]))
            else:
                self.knownWaypoints[i] = (int(self.knownWaypoints[i][0] - 1), int(self.knownWaypoints[i][1]))
            if self.knownWaypoints[i][1] == 0:
                self.knownWaypoints[i] = (int(self.knownWaypoints[i][0]), int(self.knownWaypoints[i][1] + 1))
            else:
                self.knownWaypoints[i] = (int(self.knownWaypoints[i][0]), int(self.knownWaypoints[i][1] - 1))

        for corner in self.knownWaypoints:
            if corner in self.walls:
                self.knownWaypoints.remove(corner)

        self.map = [[-1000 for y in range(self.walls[-1][1] + 1)] for x in range(self.walls[-1][0] + 1)]
        self.doOnce = False

    def getManhattanDist(self, objectA, objectB):
        """
        Returns manhattan distance between two coordinates (x, y)
        :param objectA: A tuple of (x, y) coordinates
        :param objectB: A tuple of (x, y) coordinates
        :return: distance between objectA and objectB
        """
        return int(abs(objectA[0] - objectB[0]) + abs(objectA[1] - objectB[1]))

    def getDiagonalDist(self, objectA, objectB):
        """
        Returns diagonal distance between two coordinates (x, y).
        Utilizes Pythagorean theorem.
        :param objectA: A tuple of (x, y) coordinates
        :param objectB: A tuple of (x, y) coordinates
        :return: distance between objectA and objectB
        """
        return math.sqrt((objectA[0] - objectB[0]) ** 2 + (objectA[1] - objectB[1]) ** 2)

    def getAction(self, state):
        # updates information about its' environment
        self.renewInformation(state)
        # Once per game
        if self.doOnce:
            self.instantiateNormalizeOnce(state)

        return api.makeMove(self.reEvaluateState(), self.legalDirections)

class PartialAgent(Agent):
    def __init__(self):
        """
        Initialization of parameters
        """
        self.doOnce = True
        self.lastDirection = Directions.STOP
        self.lastSpot = None
        self.position = None
        self.walls = None
        self.legalDirections = None
        self.knownGhosts = None
        self.knownWaypoints = []
        self.visitedWaypoints = []
        self.knownFood = None
        self.offsetDirectionalMapping = None
        self.oppositeOf = None
        self.ranFromGhost = False

    def final(self, state):
        """
        Runs in between games.
        Resets knowledge about the world to the starting point.
        """
        self.doOnce = True
        self.lastDirection = Directions.STOP
        self.lastSpot = None
        self.position = None
        self.walls = None
        self.legalDirections = None
        self.knownGhosts = None
        self.knownWaypoints = []
        self.visitedWaypoints = []
        self.knownFood = None
        self.offsetDirectionalMapping = None
        self.oppositeOf = None
        self.ranFromGhost = False
        print "Did I win? I hope I did. Of course I did! I am confident in myself!"


    def renewInformation(self, state):
        """
        Run at every tick.
        Pacman updates its' knowledge about the world/environment
        """
        self.position = api.whereAmI(state)

        self.legalDirections = api.legalActions(state)
        if Directions.STOP in self.legalDirections:
            self.legalDirections.remove(Directions.STOP)

        self.knownGhosts = api.ghosts(state)
        self.knownFood = api.food(state)

        for waypoint in self.knownWaypoints:
            if self.getManhattanDist(self.position, waypoint) == 0:
                self.knownWaypoints.remove(waypoint)

        if len(self.knownFood) > 0:
            for i in range(len(self.knownFood)):
                if self.knownFood[i] not in self.knownWaypoints:
                    self.knownWaypoints.append(self.knownFood[i])

    def instantiateNormalizeOnce(self, state):
        """
        Runs only once per pacman game.
        Instantiates static information that is true at the time of environment creation and ever since that point.
        Normalizes corner tuples into reachable spots (since api.corners(state) returns corners that are indeed walls.)
        If, for whatever reason, the normalized corner coordinates are inside the array of known wall coordinates (meaning
        maybe there is a double wall around the corner, or layout is not rectangular) then Pacman scraps such corners from
        knownWaypoints array.
        """
        self.walls = api.walls(state)
        self.knownWaypoints = api.corners(state)
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
        for i in range(len(self.knownWaypoints)):
            if self.knownWaypoints[i][0] == 0:
                self.knownWaypoints[i] = (int(self.knownWaypoints[i][0] + 1), int(self.knownWaypoints[i][1]))
            else:
                self.knownWaypoints[i] = (int(self.knownWaypoints[i][0] - 1), int(self.knownWaypoints[i][1]))
            if self.knownWaypoints[i][1] == 0:
                self.knownWaypoints[i] = (int(self.knownWaypoints[i][0]), int(self.knownWaypoints[i][1] + 1))
            else:
                self.knownWaypoints[i] = (int(self.knownWaypoints[i][0]), int(self.knownWaypoints[i][1] - 1))

        for corner in self.knownWaypoints:
            if corner in self.walls:
                self.knownWaypoints.remove(corner)
        self.doOnce = False

    def sortCoordsByDistance(self, coordList, distList):
        """
        Sorts a list of coordinates (array of tuples) by their distance from pacman.
        Sorting algorithm is Shell Sort.
        :param coordList: List of coordinates that need sorting
        :param distList: List of distances of each of the coordinates. Index of each coordinate must correspond to
        the index in the distance list
        """
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
        """
        Returns manhattan distance between two coordinates (x, y)
        :param objectA: A tuple of (x, y) coordinates
        :param objectB: A tuple of (x, y) coordinates
        :return: distance between objectA and objectB
        """
        return int(abs(objectA[0] - objectB[0]) + abs(objectA[1] - objectB[1]))

    def getDiagonalDist(self, objectA, objectB):
        """
        Returns diagonal distance between two coordinates (x, y).
        Utilizes Pythagorean theorem.
        :param objectA: A tuple of (x, y) coordinates
        :param objectB: A tuple of (x, y) coordinates
        :return: distance between objectA and objectB
        """
        return math.sqrt((objectA[0] - objectB[0]) ** 2 + (objectA[1] - objectB[1]) ** 2)

    def wallInBetweenPacman(self, object):
        """
        Checks if there is a wall between Pacman and an Object that is exactly 2 units away.
        :param object: A tuple of (x, y) coordinates
        :return: True if object is behind a wall, False otherwise

        In order to do this, manhattan distance must be equal to 2.
        After calculating difference in coordinates (possible results = [(0, 1); (1, 0); (1, 1)])
        We check if the difference in coordinates is perpendicular to Pacman's position ((1, 1) means that it's diagonal,
        and that the object we have is not behind a wall, but instead right around a corner at a junction)
        Only if the difference in coordinates is perpendicular to Pacman's position we can calculate the supposed spot's
        in between pacman and the object coordinates.
        Finally, we check if such coordinates exist in our known array of wall coordinates.
        """
        if self.getManhattanDist(object, self.position) == 2:
            spotDifference = (int(object[0] - self.position[0]), int(object[1] - self.position[1]))
            if spotDifference[0] == 0 or spotDifference[1] == 0:
                spotInBetween = tuple(map(sum, zip(self.position, spotDifference)))
                spotInBetween = (int(spotInBetween[0]), int(spotInBetween[1]))
                if spotInBetween in self.walls:
                    return True
        return False

    def getDangerousGhosts(self):
        """
        If there are any dangerous ghosts in near vicinity, adds them to array of objects to return.
        Ghost is not dangerous if he is behind a wall.
        :return: Array of size 0 to N.
        """
        dangerousGhosts = []
        if len(self.knownGhosts) > 0:
            ghostDistances = []
            for ghost in self.knownGhosts:
                ghostDistances.append(self.getManhattanDist(self.position, ghost))
            self.sortCoordsByDistance(self.knownGhosts, ghostDistances)
            for ghost in self.knownGhosts:
                if not self.wallInBetweenPacman(ghost):
                    dangerousGhosts.append(ghost)
        return dangerousGhosts

    def getClosestWaypoint(self):
        """
        Sorts list of knownWaypoints by each waypoint's distance accordingly.
        :return: Closest waypoint (first element of sorted list). Tuple of (x, y) values.
        """
        closest = None
        waypointDistances = []
        if len(self.knownWaypoints) > 0:
            for waypoint in self.knownWaypoints:
                waypointDistances.append(self.getManhattanDist(self.position, waypoint))
            self.sortCoordsByDistance(self.knownWaypoints, waypointDistances)
            closest = self.knownWaypoints[0]
        return closest

    def runAway(self, runFrom):
        """
        Function utilizes Voting mechanism to determine best direction. Best direction is the one which has longest overall
        distance from all objects (ghost(s)) taken into consideration.
        :param runFrom: Array of objects to run from.
        :return: Best direction to run from an object (e.g. ghost, or multiple of them). In the case of 0 objects
        in array, then choose randomly from legal directions.
        """
        if len(runFrom) == 0:
            return random.choice(self.legalDirections)

        # if there is only one legal direction (Pacman has hit a dead end) AND moving in that directions means being eaten
        # by a ghost (ghost is right behind Pacman) then best Pacman can do is STOP and pray to god ghost turns around.
        # Note: Ghost list is already sorted before entering this function.
        if len(self.legalDirections) == 1 and tuple(map(sum, zip(self.offsetDirectionalMapping[self.legalDirections[0]], self.position))) == runFrom[0]:
            return Directions.STOP

        voteNextMove = {
            Directions.NORTH: 0,
            Directions.WEST: 0,
            Directions.EAST: 0,
            Directions.SOUTH: 0
        }

        for ghost in runFrom:
            for direction in self.legalDirections:
                nextSpot = tuple(map(sum, zip(self.offsetDirectionalMapping[direction], self.position)))
                nextSpotDistanceToGhost = self.getDiagonalDist(nextSpot, ghost)
                voteNextMove[direction] += nextSpotDistanceToGhost

        # Determine which direction (Key in voteNextMove Dictionary) has max value
        bestDirection = max(voteNextMove.iteritems(), key=operator.itemgetter(1))[0]

        self.lastSpot = self.position
        self.lastDirection = bestDirection
        self.ranFromGhost = True
        return bestDirection

    def runTowards(self, runTo):
        """
        Utilizing voting mechanism, function calculates which direction has least amount of votes (meaning smallest distance)
        Prefers to not go backwards.
        :param runTo: Coordinate that pacman wants to reach
        :return: best direction
        """
        if runTo == None or len(runTo) != 2:
            return random.choice(self.legalDirections)

        voteNextMove = {
            Directions.NORTH: sys.maxint,
            Directions.WEST: sys.maxint,
            Directions.EAST: sys.maxint,
            Directions.SOUTH: sys.maxint
        }

        for direction in self.legalDirections:
            nextSpot = tuple(map(sum, zip(self.offsetDirectionalMapping[direction], self.position)))
            nextSpotDistanceToObject = self.getDiagonalDist(nextSpot, runTo)
            voteNextMove[direction] = nextSpotDistanceToObject

        # Determine which direction (Key in voteNextMove Dictionary) has min value
        bestDirection = min(voteNextMove.iteritems(), key=operator.itemgetter(1))[0]
        # We want to avoid Pacman going in an endless loop forward and backwards, cycling between 2 spots.
        # The only occassion when we can afford this, is if Pacman was running away from ghost, yet Pacman doesn't
        # hear ghost chasing it.
        # Otherwise, Pacman chooses second best direction
        if len(self.legalDirections) > 1 and self.lastDirection != Directions.STOP and bestDirection == self.oppositeOf[self.lastDirection] and not self.ranFromGhost:
            voteNextMove.pop(bestDirection)
            bestDirection = min(voteNextMove.iteritems(), key=operator.itemgetter(1))[0]

        self.lastDirection = bestDirection
        self.lastSpot = self.position
        self.ranFromGhost = False
        return bestDirection

    def getAction(self, state):
        # Once per game
        if self.doOnce:
            self.instantiateNormalizeOnce(state)

        # updates information about its' environment
        self.renewInformation(state)

        # Determines if pacman is in danger. Makes appropriate move.
        dangerousGhosts = self.getDangerousGhosts()
        if len(dangerousGhosts) > 0:
            # Algorithm supports N number of ghosts where N > 0
            bestDirection = self.runAway(dangerousGhosts)
            return api.makeMove(bestDirection, self.legalDirections)

        # If not in danger tries to remember memorized waypoints.
        # Makes appropriate move.
        closestWaypoint = self.getClosestWaypoint()
        if closestWaypoint != None:
            bestDirection = self.runTowards(closestWaypoint)
            return api.makeMove(bestDirection, self.legalDirections)

        # If not in danger and every single waypoint is visited, yet game is not over,
        # Try to make a move in the last direction that Pacman went previously.
        # If such move is illegal, choose randomly out of legal directions.
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
