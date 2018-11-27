import math
import operator
import random
import sys

import deterministicApi as api
from game import Agent, Directions

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