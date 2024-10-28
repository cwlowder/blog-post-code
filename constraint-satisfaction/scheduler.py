from datetime import datetime, timedelta
from csp import CSP

def generateConsecutiveDates(start_date, end_date):
    # Parse the input dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Generate the list of consecutive dates
    date_list = []
    current_date = start
    while current_date <= end:
        date_list.append(current_date)
        current_date += timedelta(days=1)

    return date_list

def printSchedule(schedule):
    print("*"*10)
    if schedule == None:
        print("No schedule defined\n\n")
        return
    print({date.strftime("%Y-%m-%d"): val for date, val in schedule.items()})
    print("*"*10)
    print("\n")

# Variables
variables = [
    datetime.strptime(date, "%Y-%m-%d") for date in [
        "2024-11-28", # THANKSGIVING
        "2024-11-29", # BLACK_FRIDAY
        "2024-12-24", # XMAS_EVE
        "2024-12-25", # XMAS_DAY
        "2024-12-31", # NY_EVE
        "2025-01-01", # NY_DAY
    ]
]

# Domains
ALL_PEOPLE = [
    "Alice",
    "Bob",
    "Curtis"
]
domains = {day: ALL_PEOPLE for day in variables}

# Make sure that the same person is not assigned to two days in a row
def noConsecutiveDaysConstraint(var, value, assignment):
    # First check before the set date
    yesterday = var - timedelta(days=1)
    if yesterday in assignment and assignment[yesterday] == value:
        return False
    # Next check after the set date
    tomorrow = var + timedelta(days=1)
    if tomorrow in assignment and assignment[tomorrow] == value:
        return False
    return True

# Makes sure that no one is assigned to too many days
def maxDaysConstraint(var, value, assignment):
    global variables, ALL_PEOPLE
    count = 0
    for day in variables:
        if day != var and day in assignment:
            if assignment[day] == value:
                count += 1
    # Make sure no one is assigned to too many days
    return count <= len(variables) / len(ALL_PEOPLE)

# Makes sure that everyone is assigned to atleast 5 days
def minDaysConstraint(var, value, assignment):
    global ALL_PEOPLE, variables
    # Cannot enforce constraint until every day is assigned
    if len(assignment) < len(variables):
        return True

    for person in ALL_PEOPLE:
        count = 0
        for day, assignee in assignment.items():
            if assignee == person:
                count += 1
        if count < 5:
            return False

    return True

# Takes a map of days to list of people that are unavailable to work
def unavailableConstraint(unavailable):
    def fn(var, value, assignment):
        count = 0
        day = var.strftime("%Y-%m-%d")
        if day in unavailable:
            # Check if person is unavailable to work that day
            if value in unavailable[day]:
                return False
        return True
    return fn

# Makes sure that no one is assigned to more than 1 major holiday
def onlyOneHolidayConstraint(var, value, assignment):
    holidays = [
        datetime.strptime(date, "%Y-%m-%d") for date in [
            "2024-11-28", # THANKSGIVING
            "2024-11-29", # BLACK_FRIDAY
            "2024-12-24", # XMAS_EVE
            "2024-12-25", # XMAS_DAY
            "2024-12-31", # NY_EVE
            "2025-01-01", # NY_DAY
        ]
    ]

    # Only run constraint on holidays
    if var not in holidays:
        return True

    for holiday in holidays:
        if holiday != var and holiday in assignment:
            if assignment[holiday] == value:
                return False

    return True

# Step 1
print("Step 1 - No Constraints")
csp = CSP(variables, domains)
sol = csp.solve()

printSchedule(sol)

# Step 2
print("Step 2 - No Consecutive Days Scheduled")
constraints = [
    noConsecutiveDaysConstraint
]
csp = CSP(variables, domains, constraints)
sol = csp.solve()

printSchedule(sol)

# Step 3
print("Step 3 - Max Days Scheduled per Person")
constraints = [
    noConsecutiveDaysConstraint,
    maxDaysConstraint
]
csp = CSP(variables, domains, constraints)
sol = csp.solve()

printSchedule(sol)

# Step 4
print("Step 4 - Unavailable Days")
constraints = [
    noConsecutiveDaysConstraint,
    maxDaysConstraint,
    unavailableConstraint({
        "2024-11-28": ["Alice", "Curtis"],
        "2024-12-31": ["Bob"],
    }),
]
csp = CSP(variables, domains, constraints)
sol = csp.solve()

printSchedule(sol)

print("Step 5 - Larger Time Window")
ALL_PEOPLE += [
    "Doug",
    "Ethan",
    "Frank"
]
variables = generateConsecutiveDates("2024-11-23", "2025-01-01")
domains = {day: ALL_PEOPLE for day in variables}
constraints = [
    noConsecutiveDaysConstraint,
    maxDaysConstraint,
    unavailableConstraint({
        "2024-11-28": ["Alice", "Curtis"],
        "2024-12-31": ["Bob"],
    }),
    onlyOneHolidayConstraint,
]
csp = CSP(variables, domains, constraints)
sol = csp.solve()

printSchedule(sol)
