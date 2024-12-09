from rflearner import RFLearner
import numpy as np
import math
import itertools

class ElevatorController(RFLearner):
	def __init__(self, num_floors=5, num_elevators=2, max_capacity=2, goal_iters=1000, new_call_prob=0.3, **kwargs):
		self.num_floors = num_floors
		self.num_elevators = num_elevators
		self.max_capacity = max_capacity
		self.new_call_prob = new_call_prob

		# Number of iterations until the elevator reaches its goal
		self.goal_iters = goal_iters

		# self.goal = (2,2)
		super().__init__(**kwargs)

	def getActions(self):
		return list(itertools.product(*[[-1,0,1] for i in range(self.num_elevators)]))

	def elevator_spacing(self, lst):
		# Ensure the list has at least two elements
		if len(lst) < 2:
			return 0

		# Initialize sum of differences and the count of pairs
		total_difference = 0

		# Loop over consecutive items in the list
		for i in range(len(lst) - 1):
			total_difference += abs(lst[i] - lst[i + 1])

		# Calculate and return the average difference
		return total_difference / (len(lst) - 1)

	def reward(self, next_state):
		reward = 0
		occupancy = 0
		drop_offs = 0
		buttkick = 0
		for e in next_state[1:]:
			occupancy += e[1]
			if not e[3]:
				if e[0] in e[2]:
					drop_offs += e[2].count(e[0])
			# Don't hangout at the first floor if people have called the elevator
			if e[0] == 0 and len(next_state[0]):
				# Sometimes you need a good kick in the butt
				buttkick += 1

		return (
			-len(next_state[0])
			- occupancy
			- buttkick
			+ 10*(drop_offs**2)
			+ self.elevator_spacing([e[0] for e in next_state[1:]])/2
		)

	def reachedGoal(self, _, i):
		return i >= self.goal_iters

	def validState(self, state):
		# Check boundary conditions
		for call in state[0]:
			if call < 0 or call >= self.num_floors:
				return False
		for e in state[1:]:
			# floor, = e
			pos = e[0]
			# Elevators must be kept within bounds
			if pos < 0 or pos >= self.num_floors:
				return False
		return True

	def nextStartState(self, _):
		# Nested Tuples with the following structure
		# Floors being called on
		# Elevators
		#	 Positions
		#	 Num Occupants
		#	 Desired Floors
		#    Elevator moving flag
		return ((), *[(0, 0, (), False) for i in range(self.num_elevators)])

	def applyAction(self, current_state, action):
		# calls,_ = current_state
		new_elevators = []
		new_calls = list(current_state[0])
		for e,a in zip(current_state[1:], action):
			floor, num_occup, df, moving = e
			desired_floors = list(df)
			if a == 0:
				moving = False
				# Let people out
				while floor in desired_floors:
					desired_floors.remove(floor)
					num_occup -= 1
				# Let people in
				while floor in new_calls and num_occup < self.max_capacity:
					new_calls.remove(floor)
					if floor != 0:
						desired_floors.append(0)
					else:
						desired_floors.append(np.random.randint(1, self.num_floors-1))
					num_occup += 1
			else:
				moving = True
			floor += a
			new_elevators.append((floor, num_occup, tuple(sorted(desired_floors)), moving))

		if np.random.rand() < self.new_call_prob:
			# We are only going to have riders go to the bottom floor
			caller = np.random.randint(1,self.num_floors)
			# Don't recall any actively waiting floor or any floor with an elevator 
			if caller not in new_calls: # and caller not in [e[0] for e in new_elevators]:
				new_calls.append(caller)

		return (tuple(sorted(new_calls)), *new_elevators)


	def render(self, current_state):
		out = ""
		# calls, _ = current_state
		# e_floors = [e[0] for e in current_state[1:]]
		for floor in reversed(range(self.num_floors)):
			out += f"{floor}, {floor in current_state[0]}, {[e[0] == floor for e in current_state[1:]]}\n"

		out += "Elevators:\n"
		for e in current_state[1:]:
			out += f"floor: {e[0]} num_occup:  {e[1]}\n"
		return out

