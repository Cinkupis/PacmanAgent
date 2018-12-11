import math
import operator
import sys

import api
from game import Agent, Directions


class MDPAgent(Agent):

    # Constants
    # Good for playing with different values to test performance of Pacman.
    REWARD_CAPSULE = 1.5
    REWARD_FOOD = 1
    REWARD_STANDARD = -1
    REWARD_GHOST = -2

    PROBABILITY_FORWARDS = api.directionProb            # 80%
    PROBABILITY_SIDEWAYS = (1 - api.directionProb) / 2  # 10%
    GAMMA = 1                                           # Discount Factor

    def __init__(self):
        """
        Initialization of parameters
        """
        self.doOnce = True
        self.position = None
        self.walls = None
        self.legalDirections = None
        self.ghostList = None
        self.ghostWithTimerList = None
        self.foodList = None
        self.capsuleList = None
        self.offsetDirectionalMapping = None
        self.oppositeOf = None
        self.previousMap = []
        self.currentMap = []
        self.mapHeight = 0
        self.mapWidth = 0

    def notWall(self, square):
        """
        For readability. Returns whether square is a wall or not
        """
        return square not in self.walls

    def addTuples(self, thisTuple, direction):
        """
        For readability.
        Computes the coordinates of the next tuple if a step was made from the given
        tuple in a given direction
        :param thisTuple: A tuple of (x, y) coordinates
        :param direction:
        :return: Coordinates after making a single step from 'thisTuple' in specified 'direction'
        """
        return tuple(map(sum, zip(thisTuple, self.offsetDirectionalMapping[direction])))

    def rewardOfState(self, square):
        """
        The Reward function of given State (or square in the map in our case)
        The Rewards are constants defined above the class.
        The Reward function takes also into consideration the distance between specified square and closest ghost.
        The Standard amount is the cost of making a move.
        Based on other conditions, the overall reward may increase or decrease.
        :param square: Coordinate (x, y) in question
        :return: A value representing various circumstances associated with the square
        """
        squareToGhostDistance = sys.maxint
        pointsAtState = self.REWARD_STANDARD

        for ghost in self.ghostList:
            if squareToGhostDistance > self.getDiagonalDist(square, ghost):
                squareToGhostDistance = self.getDiagonalDist(square, ghost)
                indexOfClosestGhost = self.ghostList.index(ghost)
                if squareToGhostDistance == 0:
                    squareToGhostDistance = 1
        """
        If the square is close to the ghost and ghost is either not edible or very close to becoming non-edible
        then we add a fraction of REWARD_GHOST based on the distance.
        
        Checking for distance less than 5 => thats the difference maker to prioritize the safer food and not lock
        yourself in a dead end (e.g. in smallGrid prioritizes to eat food in the corner first before going for center)
        """
        if self.ghostWithTimerList[indexOfClosestGhost][1] < 4 and squareToGhostDistance < 4:
            pointsAtState += self.REWARD_GHOST / squareToGhostDistance

        if square in self.ghostList:
            index = self.ghostList.index(square)
            if self.ghostWithTimerList[index][1] < 4:
                pointsAtState += self.REWARD_GHOST

        if square in self.capsuleList and self.shouldPacmanFocusCapsules():
            pointsAtState += self.REWARD_CAPSULE

        if square in self.foodList:
            pointsAtState += self.REWARD_FOOD

        return pointsAtState

    def shouldPacmanFocusCapsules(self):
        """
        If half (or less) of the ghosts are scared (compared to total), then focuses on eating capsules.
        Goal is to prolong capsule duration, when Pacman is safe, so as to not just rush from one corner to the other.
        :return: True or False depending on above condition.
        """
        totalGhostCount = len(self.ghostList)
        scaredGhostCount = 0
        for ghost in self.ghostWithTimerList:
            if ghost[1] > 5:
                scaredGhostCount += 1

        return scaredGhostCount <= totalGhostCount / 2

    def getDiagonalDist(self, objectA, objectB):
        """
        Returns diagonal distance between two coordinates (x, y).
        Utilizes Pythagorean theorem.
        :param objectA: A tuple of (x, y) coordinates
        :param objectB: A tuple of (x, y) coordinates
        :return: distance between objectA and objectB
        """
        return math.sqrt((objectA[0] - objectB[0]) ** 2 + (objectA[1] - objectB[1]) ** 2)

    def calculateUtilityForwads(self, currentSpot, direction):
        """
        Responsible for calculating the utility of going forwards from a certain square.
        Takes into account the fact that due to a wall being there, it may stay at the
        same square and not move at all.
        :param currentSpot: A tuple of (x, y) corresponding to square in the map
        :param direction: The forwards direction that has 80% chance of happening
        :return: Utility of moving sideways of desired direction
        """
        forwardSpot = self.addTuples(currentSpot, direction)
        if self.notWall(forwardSpot):
            x = forwardSpot[0]
            y = forwardSpot[1]
        else:
            x = currentSpot[0]
            y = currentSpot[1]
        return self.PROBABILITY_FORWARDS * self.previousMap[x][y]

    def calculateUtilitySideways(self, currentSpot, direction):
        """
        Responsible for calculating the utility of going sideways from a certain square.
        Takes into account the fact that due to a wall being there, it may stay at the
        same square and not move at all.
        :param currentSpot: A tuple of (x, y) corresponding to square in the map
        :param direction: The sideways direction that has 10% chance of happening
        :return: Utility of moving sideways of desired direction
        """
        sidewaysSpot = self.addTuples(currentSpot, direction)
        if self.notWall(sidewaysSpot):
            x = sidewaysSpot[0]
            y = sidewaysSpot[1]
        else:
            x = currentSpot[0]
            y = currentSpot[1]
        return self.PROBABILITY_SIDEWAYS * self.previousMap[x][y]

    def calculateUtility(self, currentSpot):
        """
        Responsible for calculating the utility of going forwards from a certain square.
        Takes into account the fact that due to a wall being there, it may stay at the
        same square and not move at all.
        :param currentSpot: A tuple of (x, y) corresponding to square in the map
        :return: Utility of moving sideways of desired direction
        """
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
        self.currentMap[x][y] = self.GAMMA * maxUtility + self.rewardOfState(currentSpot)

    def iterateOnce(self):
        """
        A single full iteration of the whole map.
        Assumption here is that each map is fully closed (Pacman cannot 'exit' the map)
        So naturally the outer edges of the map are walls. This means we only have to consider what is
        inside the rectangular map => saves us computation time (even a little is enough)
        """
        for y in range(1, self.mapHeight - 1):
            for x in range(1, self.mapWidth - 1):
                currentSpot = (x, y)
                if self.notWall(currentSpot):
                    self.calculateUtility(currentSpot)
                else:
                    self.currentMap[x][y] = self.previousMap[x][y]

    def runFixedNumberOfIterations(self):
        """
        Runs a number of iterations over the map.
        The number scales based on layout's dimensions.
        -l mediumClassic: 31 times
        -l smallGrid: 14 times
        """
        for x in range(self.mapHeight + self.mapWidth):
            self.iterateOnce()
            self.previousMap = self.currentMap

    def directionWithMaximumExpectedUtility(self):
        """
        Calculates which direction gives the Maximum Expected Utility for Pacman
        :return: Direction for Pacman to make.
        """
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

        self.ghostList = api.ghosts(state)
        self.ghostWithTimerList = api.ghostStatesWithTimes(state)
        self.foodList = api.food(state)
        self.capsuleList = api.capsules(state)

        self.initializeMap()

    def initializeMap(self):
        # Python doesn't have a simple initialization of 2D arrays like, for example, in Java 'int var = new int[][];'
        # So we have to resolve to fancy one liners to do the trick.
        # In this case we initialize every single square of the map to -1000. This value indicates there is a wall.
        # Later on, we adjust the values for squares that aren't exactly walls.
        self.previousMap = [[0 if self.notWall((x, y))
                             else -10
                             for y in range(self.mapHeight)]
                            for x in range(self.mapWidth)]
        self.currentMap = self.previousMap

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
        self.mapWidth = self.walls[-1][0] + 1
        self.mapHeight = self.walls[-1][1] + 1
        self.doOnce = False

    def getAction(self, state):
        # Once per game, some static info
        if self.doOnce:
            self.instantiateOnce(state)

        # updates information about its' environment
        self.renewInformation(state)

        self.runFixedNumberOfIterations()
        bestDirection = self.directionWithMaximumExpectedUtility()

        return api.makeMove(bestDirection, self.legalDirections)

    def final(self, state):
        """
        Runs in between games.
        Resets knowledge about the world to the starting point.
        """
        self.doOnce = True
        self.position = None
        self.walls = None
        self.legalDirections = None
        self.ghostList = None
        self.ghostWithTimerList = None
        self.foodList = None
        self.capsuleList = None
        self.offsetDirectionalMapping = None
        self.oppositeOf = None
        self.previousMap = []
        self.currentMap = []
        self.mapHeight = 0
        self.mapWidth = 0