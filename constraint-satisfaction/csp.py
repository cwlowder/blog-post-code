import random

class CSP:
    def __init__(self, variables, domains, constraints=[]):
        self.variables = variables
        self.domains = domains
        self.constraints = constraints
        self.solution = None

    def solve(self):
        assignment = {}
        self.solution = self.backtrack(assignment)
        return self.solution

    def backtrack(self, assignment):
        # Base case - no unnasigned variables left
        if len(assignment) == len(self.variables):
            # Run constraint checks one last time
            for var in self.variables:
                if not self.checkConstraints(var, assignment[var], assignment):
                    return None
            return assignment

        var = self.findUnassignedVar(assignment)
        for value in self.getDomainVals(var, assignment):
            if self.checkConstraints(var, value, assignment):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                del assignment[var]
        return None

    def findUnassignedVar(self, assignment):
        unassigned_vars = [var for var in self.variables if var not in assignment]

        # Find whichever unassigned var has the smallest domain
        return min(unassigned_vars, key=lambda var: len(self.domains[var]))

    def getDomainVals(self, var, assignment):
        # Copy and then shuffle domains randomly,
        # this keeps things fair and prevents
        # us from getting stuck
        domains = list(self.domains[var])
        random.shuffle(domains)
        return domains

    def checkConstraints(self, var, value, assignment):
        for constraintFn in self.constraints:
            if not constraintFn(var, value, assignment):
                return False
        return True
