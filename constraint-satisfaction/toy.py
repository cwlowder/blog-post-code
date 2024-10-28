from csp import CSP

variables = [i for i in range(3)]
domains = {var: ['Red', 'Blue'] for var in variables}

# Check that no element neighbors the same color
def neighborConstraint(var, value, assignment):
	# Check left neighbor
	if var - 1 in variables:
		if var - 1 in assignment and assignment[var - 1] == value:
			return False

	# Check Right neighbor
	if var + 1 in variables:
		if var + 1 in assignment and assignment[var + 1] == value:
			return False

	return True

# Constraints
constraints = [
    neighborConstraint
]

print("*"*7, "Solution", "*"*7)
csp = CSP(variables, domains, constraints)
sol = csp.solve()

# Blank Solution
solution = ['' for i in range(3)]
for i in sol:
	solution[i] = sol[i]

print(' '.join(solution))