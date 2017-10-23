

from __future__ import division
from random import random, randint
import sys, os, inspect
from jmoo_objective import *
from jmoo_decision import *
from jmoo_problem import jmoo_problem
from Requirement import Requirement
from Client import Client
from Release import Release
import numpy as np


class MONRP(jmoo_problem):
    def __init__(self, requirements, releases, clients, density, budget):
        self.name = "MONRP_" + str(requirements) + "_" + str(releases) + "_" + str(clients) + "_" +str(density) \
                    + "_" + str(budget)
        names = ["x"+str(i+1) for i in range(requirements)] # |x_i + y_i|
        lows =  [-1 for i in xrange(requirements)]
        ups =   [(releases-1) for _ in xrange(requirements)]
        self.decisions = [jmoo_decision(names[i], lows[i], ups[i]) for i in range(requirements)]
        self.objectives = [jmoo_objective("f1", True), jmoo_objective("f2", True), jmoo_objective("f3", True)]
        self.trequirements = requirements
        self.treleases = releases
        self.tclients = clients
        self.tdensity = density
        self.tbudget = budget
        self.requirement = None
        self.client = None
        self.release = None
        self.precedence = []
        self.generate_data()

    def generate_precedence(self):
        precedence = [[0 for _ in xrange(self.trequirements)] for _ in xrange(self.trequirements)]
        temp = []
        for _ in xrange(int(self.tdensity * self.trequirements * 0.01)):
            while True:
                row = randint(0, self.trequirements -1)
                col = randint(0, self.trequirements -1)
                t = row * 1000 + col
                if t not in temp:
                    temp.append(t)
                    break
        # print "Done"
        for t in temp:
            precedence[int(t/1000)][int(t%1000)] = 1
        return precedence

    def generate_data(self):
        self.requirement = [Requirement(i) for i in xrange(self.trequirements)]
        self.client = [Client(i, self.trequirements) for i in xrange(self.tclients)]
        budget_release = int((sum(req.cost for req in self.requirement) * (self.tbudget/100))/self.treleases)
        self.release = [Release(i, budget_release) for i in xrange(self.treleases)]
        self.precedence = self.generate_precedence()

    def print_data(i):
        print [c.weight for c in i.client]
        for p in i.precedence:
            print p
        for r in i.requirement:
            print r.cost, r.risk
        for c in i.client:
            print c.importance
        print [r.budget for r in i.release]

    def constraint1(self, x_i, y_i):
        cost = [0 for _ in xrange(self.treleases)]
        for i, y in enumerate(y_i):
            if y != 0:
                assert(self.requirement[y].id == y), "Indexing Error!"
                assert(x_i[i] <= self.treleases)
                cost[x_i[i]] += self.requirement[i].cost
        # print cost, [b.budget for b in self.release], sum(cost), sum([b.budget for b in self.release])
        extra = 0
        for c, b in zip(cost, self.release):
            if c > b.budget:
                extra -= (c - b.budget)
        return extra

    def constraint2(self, x_i, y_i):
        for y in y_i:
            if y != 0:
                relation = self.precedence[y]
                if sum(relation) == 0:  # no dependencies
                    return True
                else:
                    current_release = x_i[y] # when was y implement
                    for count, p in enumerate(relation):
                        if p != 0:
                            # the dependency 'count' wasn't implemented before current release
                            if x_i[count] > current_release:
                                return False
                    return True

    def evaluate(self, input = None):

        if input:
            input = input[:self.trequirements]
            x_i = [int(round(float(no), 0)) for no in input]  # when is r_i is implemented
            y_i = [1 if x != -1 else 0 for x in x_i]  # whether r_i would be implemented
            assert(len(x_i) == len(y_i)), "Both the list should be of the same size"
            temp = self.constraint1(x_i, y_i)  # This is dirty need to know a better trick
            # if temp != 0:
            #     assert(False), "boom"
            #     return [1e32-temp, 1e32, 1e32]
            # elif self.constraint2(x_i, y_i) is False:
            #     assert(False), "boom"
            #     return [1e32, 1e32, 1e32]
            if 1==0:
                print "this is workaround. delete it"
            else:
                return_score = 0
                cost = 0
                for i in xrange(self.trequirements):
                    score = sum([j.importance[i] * j.weight for j in self.client])
                    x = x_i[i]
                    return_score += (score * (self.treleases - x + 1) - self.requirement[i].risk) * y_i[i]
                    # reduce the cost (from A Study of the Multi-Objective Next Release Problem)
                    cost += self.requirement[i].cost * y_i[i] # whether the requirement was implemented

                # Maximize the satisfaction (from A Study of the Multi-Objective Next Release Problem)
                satisfaction = 0
                for c in xrange(self.tclients):
                    for i in xrange(self.trequirements):
                        if y_i[i] != 0:
                            satisfaction += self.client[c].importance[i]
                return [1e5-return_score, cost, 1e5-satisfaction]
        else:
            assert(False), "BOOM"
            exit()

    def generateInput(self, center=False):
        while True: # repeat if we don't meet constraints
            temp_value = []

            for decision in self.decisions:
                temp_value.append(np.random.uniform(decision.low, decision.up))
            if self.validate(temp_value) is True and self.evalConstraints(temp_value) is True: break

        assert(self.validate(temp_value) is True), "Something's wrong"
        return [int(round(float(no), 0)) for no in temp_value]

    def evalConstraints(self,input = None):
        if input:
            input = input[:self.trequirements]
            x_i = [int(round(float(no), 0)) for no in input]  # when is r_i is implemented
            y_i = [1 if x != -1 else 0 for x in x_i]  # whether r_i would be implemented
            assert(len(x_i) == len(y_i)), "Both the list should be of the same size"
            temp = self.constraint1(x_i, y_i)
            c1 = True if temp >= 0 else False  # This is dirty need to know a better trick
            c2 = self.constraint2(x_i, y_i)
            return c1 and c2
        else:
            return False

    def evalConstraintOverages(self, input=None):
        if input:
            x_i = [int(round(float(no), 0)) for no in input]  # when is r_i is implemented
            y_i = [1 if x != -1 else 0 for x in x_i]  # whether r_i would be implemented
            assert (len(x_i) == len(y_i)), "Both the list should be of the same size"
            temp = self.constraint1(x_i, y_i)
            return [temp]



if __name__ == "__main__":
    problem = MONRP(50, 5, 5, 0, 80)
    problem.generate_data()
    problem.print_data()







