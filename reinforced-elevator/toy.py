from rflearner import RFLearner
import numpy as np
import math

class ToyProblem(RFLearner):
	def __init__(self, board="", **kwargs):
		self.environment = board.strip().split('\n')

		self.height = len(self.environment)
		self.width = len(self.environment[0])

		for y, row in enumerate(self.environment):
			x = row.find('F')

			if x >= 0:
				self.goal = (x,y)
				break

		# self.goal = (2,2)
		super().__init__(**kwargs)

	def getActions(self):
		return ["up", "left", "right", "down"]

	def reward(self, next_state):
		# Bonking a wall is bad
		if self.goal == next_state:
			return 100

		# Pythagorous
		return (
			-1 * math.sqrt(
				(next_state[0] - self.goal[0])**2
				+
				(next_state[1] - self.goal[1])**2
			)
		)
		# return 0

	def reachedGoal(self, state, _):
		return state == self.goal

	def validState(self, state):
		# Check boundary conditions
		if state[0] < 0 or state[0] >= self.width:
			return False
		if state[1] < 0 or state[1] >= self.height:
			return False
		# Check position does not contain a wall
		if self.environment[state[1]][state[0]] == '#':
			return False
		return True


	def nextStartState(self, _):
		# Pick a random x,y coord and check if it is a wall
		# repeat until a good position is found
		while True:
			x = np.random.randint(self.width)
			y = np.random.randint(self.height)
			if self.environment[y][x] != "#":
				return (x,y)

	def applyAction(self, current_state, a):
		if a == "up":
			return (current_state[0], current_state[1] - 1)
		elif a == "down":
			return (current_state[0], current_state[1] + 1)
		elif a == "left":
			return (current_state[0] - 1, current_state[1])
		elif a == "right":
			return (current_state[0] + 1, current_state[1])

	def render(self, current_state):
		e = self.environment
		out = [c for c in '\n'.join(e)]
		(x, y) = current_state
		out[x+y*(self.width+1)] = '!'
		return ''.join(out)

board = """
__#____
__#_#_F
__#_###
__#____
_####_#
_#_#___
_______ 
"""
# board = """
# ___
# ___
# __F
# """
tp = ToyProblem(board=board, exploration_prob=0.9, epochs=1000)

tp.train()
# Rerun to show solution
print("RESTARTING")

# tp.exploration_prob = 0

for state in tp.run((0,0)):
	print("="*tp.width)
	print(tp.render(state))

