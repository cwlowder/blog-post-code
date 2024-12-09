from abc import ABC, abstractmethod
from typing import final
import numpy as np
import math
import sys
import pickle

def progress_bar(iterable, epochs, prefix="", length=40, fill="█"):
    total = epochs
    def print_bar(iteration):
        percent = ("{0:.1f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        sys.stdout.write(f'\r{prefix} |{bar}| {percent}% Complete')
        sys.stdout.flush()

    for i, item in enumerate(iterable):
        print_bar(i + 1)
        yield item
    sys.stdout.write("\n")  # Ensure newline after progress completion


class RFLearner(ABC):
	def __init__(self, learning_rate=0.8, discount_factor=0.95, exploration_prob=0.2, epochs=1000):
		self.learning_rate = learning_rate
		self.discount_factor = discount_factor
		self.exploration_prob = exploration_prob
		self.epochs = epochs

		self._actions = self.getActions()
		
		self.Q_table = {} # np.zeros((self.totalNumStates(), len(self._actions)))

		# # Check phase conversions before continuing
		# pigeons = set()
		# for _ in range(1000):
		# 	s = self.randomState()
		# 	u = self.fromPhaseSpace(s)
		# 	b = self.toPhaseSpace(u)
		# 	assert s == b, f"Failed phase conversion: {s} to {u} to {b} ({s} != {b})"
		# pass

	@abstractmethod
	def getActions(self):
		# Returns list of actions
		pass

	# @abstractmethod
	# def fromPhaseSpace(self, idx):
	# 	# Converts from phase space to user space
	# 	pass

	@abstractmethod
	def reward(self, user_state):
		pass

	@abstractmethod
	def reachedGoal(self, user_state, counter):
		# Define if learner has reached goal
		# includes counter for how many cycles we have run
		pass

	# @final
	# def finished(self, phase_state):
	# 	return self.reachedGoal(self.fromPhaseSpace(phase_state))

	@abstractmethod
	def applyAction(self, user_state, a):
		# Apply action to current state
		pass

	@abstractmethod
	def nextStartState(self, epoch):
		# Returns the next start user state to use
		pass

	def _applyAction(self, user_state, a):		
		if a < 0 or a > len(self._actions):
			raise Exception(f"Action not in list of actions: {a}")
		next_state = self.applyAction(user_state, self._actions[a])
		if self._validState(next_state):
			return next_state
		return False

	@final
	def save(self, filename="model.pkl"):
		with open(filename, "wb") as f:
			pickle.dump(self.Q_table, f)

	@final
	def load(self, filename="model.pkl"):
		with open(filename, "rb") as f:
			self.Q_table = pickle.load(f)

	@final
	def train(self):
		# for epoch in range(self.epochs):
		for epoch in progress_bar(range(self.epochs), self.epochs, length=10):
			current_state = self.nextStartState(epoch)

			if current_state not in self.Q_table:
				self.Q_table[current_state] = [0 for _ in self._actions]

			counter = 0
			while not self.reachedGoal(current_state, counter):
				counter += 1

				if np.random.rand() < self.exploration_prob:
					action = np.random.randint(len(self._actions))
				else:
					action = np.argmax(self.Q_table[current_state])

				next_state = self._applyAction(current_state, action)

				# Invalid states will not be acceptable
				if next_state != False:
					if next_state not in self.Q_table:
						self.Q_table[next_state] = [0 for _ in self._actions]
					reward = self.reward(next_state)
				else:
					reward = -np.inf
					next_state = current_state


				if reward == -np.inf:
					# Illegal rewards are gonna be negatively encouraged
					self.Q_table[current_state][action] = -np.inf
				else:
					self.Q_table[current_state][action] += self.learning_rate * \
						(reward + self.discount_factor *
						 np.max(self.Q_table[next_state]) - self.Q_table[current_state][action])
					current_state = next_state

	@final
	def run(self, start_user_state=None):
		if start_user_state == None:
			start_user_state = self.nextStartState(0)

		current_state = start_user_state
		counter = 0
		while not self.reachedGoal(current_state, counter):
			counter += 1
			yield current_state
			action = np.argmax(self.Q_table[current_state])

			next_state = self._applyAction(current_state, action)
			if not self._validState(next_state):
				break
			current_state = next_state
		# Yield last step to show goal reached
		yield current_state

	@abstractmethod
	def validState(self, state):
		# Validate user state is ok
		pass

	def _validState(self, state):
		if state == False:
			return False
		return self.validState(state)