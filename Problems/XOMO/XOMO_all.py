from __future__ import division

import inspect
import os
import sys

parentdir = os.path.realpath(
    os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../")))
if parentdir not in sys.path:
    sys.path.insert(0, parentdir)
from jmoo_objective import *
from jmoo_decision import *
from jmoo_problem import jmoo_problem
from Base.xomo_liaison import xomol


class XOMO_all(jmoo_problem):
    "Xomo_all"

    def __init__(prob, percentage=-1):
        prob.percentage=percentage
        prob.name = "xomo_all"
        # Should be as xomol.names to maintain order of LOWs and UPs
        names = ["aa", "sced", "cplx", "site", "resl", "acap", "etat", "rely",
                 "Data", "prec", "pmat", "aexp", "flex", "pcon", "tool", "time",
                 "stor", "docu", "b", "plex", "pcap", "kloc", "ltex", "pr",
                 "ruse", "team", "pvol"]
        # Generic Bounds as per menzies.us/pdf/06xomo101.pdf fig.9
        bounds = {"aa": (1, 6),
                  "sced": (1.00, 1.43),
                  "cplx": (0.73, 1.74),
                  "site": (0.80, 1.22),
                  "resl": (1.41, 7.07),
                  "acap": (0.71, 1.42),
                  "etat": (1, 6),
                  "rely": (0.82, 1.26),
                  "Data": (0.90, 1.28),
                  "prec": (1.24, 6.20),
                  "pmat": (1.56, 7.80),
                  "aexp": (0.81, 1.22),
                  "flex": (1.01, 5.07),
                  "pcon": (0.81, 1.29),
                  "tool": (0.78, 1.17),
                  "time": (1.00, 1.63),
                  "stor": (1.00, 1.46),
                  "docu": (0.81, 1.23),
                  "b": (3, 10),
                  "plex": (0.85, 1.19),
                  "pcap": (0.76, 1.34),
                  "kloc": (2, 1000),
                  "ltex": (0.84, 1.20),
                  "pr": (1, 6),
                  "ruse": (0.95, 1.24),
                  "team": (1.01, 5.48),
                  "pvol": (0.87, 1.30)}
        # bounds specific to all model
        bounds_all = {"prec": (1.24, 6.2),
                      "flex": (1.01, 5.07),
                      "resl": (1.41, 7.07),
                      "team": (1.01, 5.48),
                      "pmat": (1.56, 7.8),
                      "rely": (0.82, 1.26),
                      "cplx": (0.73, 1.74),
                      "Data": (0.9, 1.14),
                      "ruse": (0.95, 1.24),
                      "time": (1, 1.63),
                      "stor": (1, 1.17),
                      "pvol": (0.87, 1.3),
                      "acap": (0.71, 1.19),
                      "pcap": (0.76, 1),
                      "pcon": (0.81, 1.29),
                      "aexp": (0.81, 1.22),
                      "plex": (0.91, 1.19),
                      "ltex": (0.84, 1.2),
                      "tool": (0.78, 1.09),
                      "sced": (1, 1.43),
                      "site": (0.8, 1.22),
                      "docu": (0.81, 1.23),
                      "kloc": (7, 418)}
        # Update main bounds with bounds of all
        for key, val in bounds_all.items():
            bounds[key] = (min(val), max(val))
            if min(val) == max(val): bounds[key] = (min(val), max(val) + 0.000001)  # To remove division by 0

        prob.decisions = [jmoo_decision(names[i], bounds[names[i]][0], bounds[names[i]][1]) for i in range(len(names))]

        prob.objectives = [jmoo_objective("Effort", True), jmoo_objective("Months", True),
                           jmoo_objective("Defects", True), jmoo_objective("Risks", True)]

    def evaluate(prob, input=None):
        if input:
            for i, decision in enumerate(prob.decisions):
                decision.value = input[i]
        else:
            input = [decision.value for decision in prob.decisions]
        xomoxo = xomol()
        output = xomoxo.run(input)
        for i, objective in enumerate(prob.objectives):
            objective.value = output[i]
        return [objective.value for objective in prob.objectives]

    def evalConstraints(prob, input=None):
        return False  # no constraints
