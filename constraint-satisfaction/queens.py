from csp import CSP

def printBoard(board):
	print("Board:")
	print()
	for y in range(8):
		print(''.join(board[y]))
	print()


# Variables - all positions will be in (y,x) coordinates
variables = [(y, x) for y in range(8) for x in range(8)]

# Domains
domains = {var: ['Q', '.'] for var in variables}


# Constraints For all directions
# ↖ ↑ ↗
# ← · →
# ↙ ↓ ↘

# Check that at most one queen is in any column ↓
def columnConstraint(var, value, assignment):
	if value != 'Q':
		return True
	for y in range(8):
		if y != var[0]:
			pos = (y, var[1])
			if pos in assignment and assignment[pos] == 'Q':
				return False
	return True

# Check that at most one queen is in any column →
def rowConstraint(var, value, assignment):
	if value != 'Q':
		return True
	for x in range(8):
		if x != var[1]:
			pos = (var[0], x)
			if pos in assignment and assignment[pos] == 'Q':
				return False
	return True

# Check that at most one queen in any diagonal
def diagonalConstraint(var, value, assignment):
	if value != 'Q':
		return True
	for i in range(1,8):
		# First check ↘
		pos = (var[0]+i, var[1]+i)
		if pos[0] < 8 and pos[1] < 8:
			if pos in assignment and assignment[pos] == 'Q':
				return False
		# Next check ↗
		pos = (var[0]-i, var[1]+i)
		if pos[0] >= 0 and pos[1] < 8:
			if pos in assignment and assignment[pos] == 'Q':
				return False
		# Next check ↖
		pos = (var[0]-i, var[1]-i)
		if pos[0] >= 0 and pos[1] >= 0:
			if pos in assignment and assignment[pos] == 'Q':
				return False
		# Lastly check ↙
		pos = (var[0]+i, var[1]-i)
		if pos[0] < 8 and pos[1] >= 0:
			if pos in assignment and assignment[pos] == 'Q':
				return False
	return True

# Check that final board has 8 queens
def eightQueensConstraint(var, value, assignment):
	count = 0
	for y in range(8):
		for x in range(8):
			if (y,x) not in assignment:
				# Only run if all points are assigned
				return True
			if assignment[(y,x)] == 'Q':
				count += 1
	# Final board must have 8 queens
	return count == 8


# Constraints
constraints = [
    columnConstraint,
    rowConstraint,
    diagonalConstraint,
    eightQueensConstraint,
]

print("*"*7, "Solution", "*"*7)
csp = CSP(variables, domains, constraints)
sol = csp.solve()

solution = [['?' for i in range(8)] for i in range(8)]
for i, j in sol:
    solution[i][j] = sol[(i, j)]


printBoard(solution)