import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import os
import pickle
import re
import nltk
import string
import logging
import sys
from dataclasses import dataclass
from collections import deque

data1 = pd.read_csv("/Users/Laura/Desktop/codingforclasses/AIcoding/cities.csv")
data2 = pd.read_csv("/Users/Laura/Desktop/codingforclasses/AIcoding/connections.csv")

'''
print(data1.head())
print(data2.head())'''
'''
source "/Users/Laura/Desktop/coding for classes/AI coding/.venv/bin/activate"
python -u "/Users/Laura/Desktop/coding for classes/AI coding/search.py"
'''

@dataclass
class Node:
	state: str
	parent: "Node | None" = None
	action: str | None = None
	path_cost: int = 0

def search():
	node = Node(state="Bucharest")
	goal_state = "Rome"
	frontier = deque([node])
	explored = set()

	while frontier:
		node = frontier.popleft()

		if node.state.casefold() == goal_state.casefold():
			return node

		explored.add(node.state.casefold())

		connections = data2[
			data2["city_from"].str.casefold() == node.state.casefold()
		]
		for connection in connections.itertuples(index=False):
			child_state = connection.city_to
			if child_state.casefold() in explored:
				continue

			child = Node(
				state=child_state,
				parent=node,
				action=f"Travel to {child_state}",
				path_cost=node.path_cost + connection.time_min,
			)
			frontier.append(child)

	return None

def get_path(node):
	path = []
	while node is not None:
		path.append(node.state)
		node = node.parent
	return list(reversed(path))

result = search()
if result is None:
	print("No path found.")
else:
	print(" -> ".join(get_path(result)))
	print(f"Total travel time: {result.path_cost} minutes")