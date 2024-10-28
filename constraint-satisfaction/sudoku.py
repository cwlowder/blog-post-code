from csp import CSP

# Define the Sudoku puzzle as a 9x9 grid
puzzle = [[5, 3, 0, 0, 7, 0, 0, 0, 0],
          [6, 0, 0, 1, 9, 5, 0, 0, 0],
          [0, 9, 8, 0, 0, 0, 0, 6, 0],
          [8, 0, 0, 0, 6, 0, 0, 0, 3],
          [4, 0, 0, 8, 0, 3, 0, 0, 1],
          [7, 0, 0, 0, 2, 0, 0, 0, 6],
          [0, 6, 0, 0, 0, 0, 2, 8, 0],
          [0, 0, 0, 4, 1, 9, 0, 0, 5],
          [0, 0, 0, 0, 8, 0, 0, 0, 0]]

# Function to display the Sudoku puzzle
def printSudoku(puzzle):
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - - ")
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")
            print(puzzle[i][j], end=" ")
        print()

# Print the initial puzzle
printSudoku(puzzle)

# Variables
variables = [(i, j) for i in range(9) for j in range(9)]

# Domains
domains = {var: list(range(1, 10)) if puzzle[var[0]][var[1]] == 0 
           else {puzzle[var[0]][var[1]]} for var in variables}

def columnConstraint(var, value, assignment):
    for y in range(9):
        if y != var[1]:
            point = (var[0], y)
            if point in assignment and assignment[point] == value:
                return False
    return True

def rowConstraint(var, value, assignment):
    for x in range(9):
        if x != var[0]:
            point = (x, var[1])
            if point in assignment and assignment[point] == value:
                return False
    return True

def subgridConstraint(var, value, assignment):
    sub_x, sub_y = var[0] // 3, var[1] // 3
    for x in range(sub_x * 3, (sub_x + 1) * 3):
        for y in range(sub_y * 3, (sub_y + 1) * 3):
            point = (x, y)
            if point != var:
                if point in assignment and assignment[point] == value:
                    return False
    return True

# Constraints
constraints = [
    columnConstraint,
    rowConstraint,
    subgridConstraint,
]

# Solve the Sudoku puzzle using CSP
print("*"*7, "Solution", "*"*7)
csp = CSP(variables, domains, constraints)
sol = csp.solve()

# Format the solution for output
solution = [[0 for i in range(9)] for i in range(9)]
for i, j in sol:
    solution[i][j] = sol[i, j]


# Print the solved Sudoku puzzle
printSudoku(solution)