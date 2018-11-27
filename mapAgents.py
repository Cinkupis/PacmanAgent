from pacman import Directions
from game import Agent
import api
import random

class Grid:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    def display(self):       
        for i in range(self.height):
            for j in range(self.width):
                print self.grid[i][j],
            print
        print

    def prettyDisplay(self):       
        for i in range(self.height):
            for j in range(self.width):
                print self.grid[self.height - (i + 1)][j],
            print
        print

    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

class MapAgent(Agent):

    def __init__(self):
        print "Running init!"

    def registerInitialState(self, state):
         print "Running registerInitialState!"
         # Make a map of the right size
         self.makeMap(state)
         self.addWallsToMap(state)
         self.updateFoodInMap(state)
         self.map.display()

    def final(self, state):
        print "Looks like I just died!"

    def makeMap(self,state):
        corners = api.corners(state)
        print corners
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height)

    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')

    def updateFoodInMap(self, state):
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    self.map.setValue(i, j, ' ')
        food = api.food(state)
        for i in range(len(food)):
            self.map.setValue(food[i][0], food[i][1], '*')

    def getAction(self, state):
        self.updateFoodInMap(state)
        self.map.prettyDisplay()

        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        return api.makeMove(random.choice(legal), legal)
    

   
