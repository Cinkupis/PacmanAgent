import random

import deterministicApi as api
import util
from game import Agent, Directions

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