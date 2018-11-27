from pacman import Directions
from game import Agent
import api
import random

class RandomAgent(Agent):

    def getAction(self, state):
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        return api.makeMove(random.choice(legal), legal)