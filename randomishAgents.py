from pacman import Directions
from game import Agent
import api
import random

class RandomishAgent(Agent):

    def __init__(self):
        self.last = Directions.STOP

    def getAction(self, state):
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        if self.last in legal:
            return api.makeMove(self.last, legal)
        else:
            pick = random.choice(legal)
            self.last = pick
            return api.makeMove(pick, legal)