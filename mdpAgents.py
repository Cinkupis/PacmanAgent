import operator
import sys
import util

import api
from game import Agent, Directions

REWARD_CAPSULE = 0.5
REWARD_FOOD = 0.5
REWARD_STANDARD = -0.5
REWARD_GHOST = -10

PROBABILITY_FORWARDS = 0.8
PROBABILITY_SIDEWAYS = 0.1

CONVERGENCE_THRESHOLD = 0
GAMMA = 0.95

class NonDeterministicAgent(Agent):

    def __init__(self):
        """
        Initialization of parameters
        """
        self.doOnce = True
        self.capsuleEaten = False
        self.position = None
        self.walls = None
        self.legalDirections = None
        self.knownGhosts = None
        self.knownGhostsWithTimer = None
        self.knownFood = None
        self.knownCapsules = None
        self.offsetDirectionalMapping = None
        self.oppositeOf = None
        self.previousMap = []
        self.currentMap = []
        self.sumOfAllUtilities = 0

    def initializeMap(self):
        for y in range(self.walls[-1][1] + 1):
            for x in range(self.walls[-1][0] + 1):
                spot = (x, y)
                if spot not in self.walls:
                    self.previousMap[x][y] = 0
        self.currentMap = self.previousMap

    def isSpotEmpty(self, spot):
        return spot not in self.walls

    def addTuples(self, thisTuple, direction):
        return tuple(map(sum, zip(thisTuple, self.offsetDirectionalMapping[direction])))

    def reward(self, spot):
        distance = 1000
        indexOfClosestGhost = None
        for ghost in self.knownGhosts:
            if distance > util.manhattanDistance(spot, ghost):
                distance = util.manhattanDistance(spot, ghost)
                indexOfClosestGhost = self.knownGhosts.index(ghost)
                if distance == 0:
                    distance = 1

        if indexOfClosestGhost != None and self.knownGhostsWithTimer[indexOfClosestGhost][1] > 0 and distance <= 2:
            return REWARD_STANDARD
        if distance < 3:
            return REWARD_GHOST / distance
        if spot in self.knownCapsules:
            return REWARD_CAPSULE
        if spot in self.knownFood:
            return REWARD_FOOD
        return REWARD_STANDARD


    def calculateUtilityForwads(self, currentSpot, direction):
        forwadsSpot = self.addTuples(currentSpot, direction)
        if forwadsSpot in self.walls:
            x = currentSpot[0]
            y = currentSpot[1]
        else:
            x = forwadsSpot[0]
            y = forwadsSpot[1]
        return PROBABILITY_FORWARDS * self.previousMap[x][y]

    def calculateUtilitySideways(self, currentSpot, direction):
        sidewaysSpot = self.addTuples(currentSpot, direction)
        if sidewaysSpot in self.walls:
            x = currentSpot[0]
            y = currentSpot[1]
        else:
            x = sidewaysSpot[0]
            y = sidewaysSpot[1]
        return PROBABILITY_SIDEWAYS * self.previousMap[x][y]

    def calculateUtility(self, currentSpot):
        x = currentSpot[0]
        y = currentSpot[1]
        allDirections = [
            Directions.NORTH,
            Directions.EAST,
            Directions.SOUTH,
            Directions.WEST
        ]
        maxUtility = -sys.maxint
        for direction in allDirections:
            utility = self.calculateUtilityForwads(currentSpot, direction)
            utility += self.calculateUtilitySideways(currentSpot, Directions.LEFT[direction])
            utility += self.calculateUtilitySideways(currentSpot, Directions.RIGHT[direction])
            if utility > maxUtility:
                maxUtility = utility
        self.currentMap[x][y] = GAMMA * maxUtility + self.reward(currentSpot)

    def iterateOnce(self):
        for y in range(1, self.walls[-1][1]):
            for x in range(1, self.walls[-1][0]):
                currentSpot = (x, y)
                if self.isSpotEmpty(currentSpot):
                    self.calculateUtility(currentSpot)
                else:
                    self.currentMap[x][y] = self.previousMap[x][y]
                self.sumOfAllUtilities += self.currentMap[x][y]

    def runIterationsUntilConverge(self):
        while True:
            previousSumOfAllUtilities = self.sumOfAllUtilities
            self.sumOfAllUtilities = 0
            self.iterateOnce()
            self.previousMap = self.currentMap
            if abs(abs(previousSumOfAllUtilities) - abs(self.sumOfAllUtilities)) <= CONVERGENCE_THRESHOLD:
                break

    def printMap(self):
        for y in range(self.walls[-1][1] + 1):
            for x in range(self.walls[-1][0] + 1):
                if self.currentMap[x][y] == -1000:
                    print self.currentMap[x][y],
                elif self.currentMap[x][y] == 5:
                    print("%.3f" % self.currentMap[x][y]),
                elif self.currentMap[x][y] == -500:
                    print self.currentMap[x][y],
                else:
                    print("%.2f" % self.currentMap[x][y]),
                print "|",
            print

    def maximumExpectedUtility(self):
        utilities = {}
        for direction in self.legalDirections:
            nextSpot = self.addTuples(self.position, direction)
            x = nextSpot[0]
            y = nextSpot[1]
            utilities[direction] = self.currentMap[x][y]
        bestDirection = max(utilities.iteritems(), key=operator.itemgetter(1))[0]
        return bestDirection

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
        self.knownGhostsWithTimer = api.ghostStatesWithTimes(state)
        self.knownFood = api.food(state)
        self.knownCapsules = api.capsules(state)

    def instantiateOnce(self, state):
        """
        Runs only once per pacman game.
        Instantiates static information that is true at the time of environment creation and ever since that point.
        """
        self.walls = api.walls(state)
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

        # Python doesn't have a simple initialization of 2D arrays like, for example, in Java 'int var = new int[][];'
        # So we have to resolve to fancy one liners to do the trick.
        # In this case we initialize every single square of the map to -1000. This value indicates there is a wall.
        # Later on, we adjust the values for squares that aren't exactly walls.
        self.previousMap = [[-1000 if (x, y) in self.walls
                             else 0
                             for y in range(self.walls[-1][1] + 1)]
                            for x in range(self.walls[-1][0] + 1)]
        self.doOnce = False

    def getAction(self, state):
        # updates information about its' environment
        self.renewInformation(state)
        # Once per game
        if self.doOnce:
            self.instantiateOnce(state)

        self.initializeMap()
        self.runIterationsUntilConverge()
        bestDirection = self.maximumExpectedUtility()

        # self.printMap()
        # print "-----------------------------------------------------------"

        return api.makeMove(bestDirection, self.legalDirections)

    def final(self, state):
        """
        Runs in between games.
        Resets knowledge about the world to the starting point.
        """
        self.doOnce = True
        self.capsuleEaten = False
        self.position = None
        self.walls = None
        self.legalDirections = None
        self.knownGhosts = None
        self.knownGhostsWithTimer = None
        self.knownFood = None
        self.knownCapsules = None
        self.offsetDirectionalMapping = None
        self.oppositeOf = None
        self.previousMap = []
        self.currentMap = []
        self.sumOfAllUtilities = 0