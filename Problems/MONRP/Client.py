from __future__ import division
from random import random, randint

class Client:
    wt_min = 0
    wt_max = 5
    def __init__(i, id, req):
        i.id = id
        i.weight = int(i.wt_min + random() * (i.wt_max - i.wt_min))
        i.importance = [randint(0,5) for _ in xrange(req)]