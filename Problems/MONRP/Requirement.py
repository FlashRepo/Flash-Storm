from __future__ import division
from random import random, randint
class Requirement:
    risk_min = 1
    risk_max = 5
    cost_min = 10
    cost_max = 20
    def __init__(i, id):
        i.id = id
        i.risk = int(i.risk_min + random() * (i.risk_max - i.risk_min))
        i.cost = int(i.cost_min + random() * (i.cost_max - i.cost_min))