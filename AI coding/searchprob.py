import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import search
import searchprob
import math
import random
import time
from collections import deque
from search import Problem

cities = pd.read_csv("/Users/Laura/Desktop/codingforclasses/AIcoding/cities.csv")
connections = pd.read_csv("/Users/Laura/Desktop/codingforclasses/AIcoding/connections.csv")

#liar our 

def actions(self, state): #gives the action I can do from a city, which is the cities that are connected to the current city
    return connections[connections['from'] == state]['to'].tolist()

def result(self, state, action): #with the given state and action, where do I end up? This is the city that is connected to the current city
    pass #return the city that is connected to the current city by the given action
'''
Finish this part of the code to return the city that is connected to the current city by the given action
'''


def is_goal(self, state):
    return state == self.goal

def action_cost(self, state, action, next_state): #determine how much does the action cost, which is the distance between the two cities
    #return the distance between the two cities or the time it takes to travel between the two cities
    if state == next_state:
        return 0
    else:
        distance = connections[(connections['from'] == state) & (connections['to'] == next_state)]['distance'].values[0]
        return distance
    '''
    Finish this part of the code to return the distance between the two cities or the time it takes to travel between the two cities
    '''
    

#complete this code give the cities we were given
#actions should be the cities that are connected to the current city -> give these