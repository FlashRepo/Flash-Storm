from jmoo_objective import *
from jmoo_decision import *
from jmoo_problem import jmoo_problem
from Helper.pom3 import pom3


class POM3B(jmoo_problem):
    "POM3B"

    def __init__(prob, percentage=-1):
        prob.percentage=percentage
        prob.name = "POM3B"
        names = ["Culture", "Criticality", "Criticality Modifier", "Initial Known", "Inter-Dependency",
                 "Dynamism", "Size", "Plan", "Team Size"]
        LOWS = [0.10, 0.82, 80, 0.40, 0,   1, 0, 0, 1]
        UPS  = [0.90, 1.26, 95, 0.70, 100, 50, 2, 5, 20]
        prob.decisions = [jmoo_decision(names[i], LOWS[i], UPS[i]) for i in range(len(names))]
        prob.objectives = [jmoo_objective("Cost", True, None, None), jmoo_objective("Score", True, 0, 1),
                           # jmoo_objective("Completion", False, 0, 1)]
                          jmoo_objective("Idle", True, None, None)]

    def evaluate(prob, input = None):
        if input:
            for i,decision in enumerate(prob.decisions):
                decision.value = input[i]
        else: input = [decision.value for decision in prob.decisions]
        p3 = pom3()
        output = p3.simulate(input)
        for i,objective in enumerate(prob.objectives):
            objective.value = output[i]
        return [objective.value for objective in prob.objectives]

    def evalConstraints(prob,input = None):
        return False #no constraints