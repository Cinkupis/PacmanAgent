import deterministicApi as api
import util
from game import Agent, Directions

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
            print util.manhattanDistance(pacman, theGhosts[i])

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
