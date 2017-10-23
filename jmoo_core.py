"""
##########################################################
### @Author Joe Krall      ###############################
### @copyright see below   ###############################

    This file is part of JMOO,
    Copyright Joe Krall, 2014.

    JMOO is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    JMOO is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with JMOO.  If not, see <http://www.gnu.org/licenses/>.
    
###                        ###############################
##########################################################
"""

"""

Random Stuff
------------

"""

import random
# from Graphics.simplified import draw_hv, draw_igd, draw_spread, draw_gd
from Graphics.simplified_new import get_performance_measures
from jmoo_jmoea import jmoo_evo
from jmoo_properties import DECISION_BIN_TABLE, DATA_SUFFIX, DATA_PREFIX, DEFECT_PREDICT_PREFIX, SUMMARY_RESULTS, \
    RRS_TABLE
from jmoo_stats_box import percentChange

import multiprocessing as mp
import os

any = random.uniform
normal = random.gauss
seed = random.seed


def readpf(problem):
    filename = "./PF/" + problem.name + "(" + str(len(problem.objectives)) + ")-PF.txt"
    f = open(filename, "r")
    true_PF = []
    for line in f:
        temp = []
        for x in line.split():
            temp.append(float(x))
        true_PF.append(temp)
    return true_PF


def sometimes(p):
    "Returns True at probability 'p;"
    return p > any(0, 1)


def one(lst):
    "Returns one item in a list, selected at random"
    return lst[int(any(0, len(lst) - 1))]


def chosen_one(problem, lst):
    def sum(ll):
        l = ll.fitness.fitness
        # print "l: ", l
        assert len(problem.objectives) == len(l), "Something is wrong here"
        new = []
        for i, o in enumerate(problem.objectives):
            if o.lismore is False:
                new.append(l[i])
            else:
                new.append(100 - l[i])
            return min(new)

    print "Length of frontier: ", len(lst)
    chosen = lst[0]

    for element in lst:
        if sum(chosen) < sum(element):
            chosen = element

    return chosen


"Brief notes"
"Core Part of JMOO accessed by jmoo_interface."

from jmoo_defect_chart import *
from joes_stats_suite import joes_stats_reporter
import time


class jmoo_stats_report:
    def __init__(self, tests, Configurations):
        self.tests = tests
        self.Configurations = Configurations

    def doit(self, tagnote=""):
        joes_stats_reporter(self.tests.problems, self.tests.algorithms, self.Configurations, tag=tagnote)


class jmoo_decision_report:
    def __init__(self, tests):
        self.tests = tests

    def doit(self, tagnote=""):
        joes_decision_reporter(self.tests.problems, self.tests.algorithms, tag=tagnote)


class jmoo_chart_report:
    def __init__(self, tests, Configurations):
        self.tests = tests
        self.Configurations = Configurations

    def doit(self, tagnote=""):
        igd_list = []
        for problem in self.tests.problems:
            get_performance_measures(problem, self.Configurations['Universal']['Population_Size'])
            # print "HyperVolume", problem.name + " Population " + str(self.Configurations['Universal']['Population_Size']),
            # draw_hv([problem], self.tests.algorithms, self.Configurations, tag="HV")
            # print "Spread", problem.name + " Population " + str(self.Configurations['Universal']['Population_Size']),
            # draw_spread([problem], self.tests.algorithms, self.Configurations, tag="SPR")
            # print "IGD"
            # draw_igd([problem], self.tests.algorithms, self.Configurations, tag="IGD")
            # print "GD"
            # draw_gd([problem], self.tests.algorithms, self.Configurations, tag="GD")


def generate_final_frontier_for_gale4(problems, algorithms, Configurations, tag=""):
    if "GALE4" not in [algorithm.name for algorithm in algorithms]: return
    else:
        for problem in problems:
            from Graphics.PerformanceMeasures.DataFrame import ProblemFrame
            data = ProblemFrame(problem, [a for a in algorithms if a.name == "GALE4"])

            # data for all repeats
            total_data = [data.get_frontier_values(gen_no) for gen_no in xrange(Configurations["Universal"]["No_of_Generations"])]

            data_for_all_generations = []
            for repeat in xrange(Configurations["Universal"]["Repeats"]):
                temp_data = []
                for gen_no in xrange(Configurations["Universal"]["No_of_Generations"]):
                    temp_data.extend(total_data[gen_no]["GALE4"][repeat])

                from jmoo_individual import jmoo_individual
                solutions = [jmoo_individual(problem, td.decisions, problem.evaluate(td.decisions)) for td in temp_data]

                # non dominated sorting
                from jmoo_algorithms import selNSGA2
                final_solutions, _ = selNSGA2(problem, [], solutions, Configurations)

                for i in xrange(Configurations["Universal"]["No_of_Generations"]):
                    filename = "./RawData/PopulationArchives/" + "GALE4" + "_" + problem.name + "/" + str(repeat) + "/" + \
                               str(i+1) + ".txt"
                    f = open(filename, "w")
                    for fs in final_solutions:
                        f.write(','.join([str(fss) for fss in fs.decisionValues]) + "," + ",".join([str(fss) for fss in fs.fitness.fitness]) + "\n")
                    f.close()




class jmoo_df_report:
    def __init__(self, tag="stats", tests=None):
        self.filename = DEFECT_PREDICT_PREFIX + "DefectPredict.xml"
        self.tag = tag
        self.tests = tests

    def doit(self, tagnote=""):
        if self.tag == "stats":
            self.doStatistics()
        elif self.tag == "Charts":
            self.doCharts()
        elif self.tag == "ranking":
            self.doRanks()

    def doStatistics(self):
        parseXML(self.filename, self.tag)

    def doCharts(self):
        parseXML(self.filename, self.tag)

    def doRanks(self):
        assert (self.tests != None), "Problems not passed"
        parseXML(self.filename, self.tag, self.tests)


class jmoo_test:
    def __init__(self, problems, algorithms):
        self.problems = problems
        self.algorithms = algorithms

    def __str__(self):
        return str(self.problems) + str(self.algorithms)


def call_jmoo_evo(problem, algorithm, configurations, repeat):
    import os
    print "Working in Process #%d" % (os.getpid())
    foldername = "./RawData/PopulationArchives/" + algorithm.name + "_" + problem.name \
                 + "_" + str(configurations["Universal"]["Population_Size"]) + "/" + str(repeat)
    import os
    if not os.path.exists(foldername):
        print foldername
        os.makedirs(foldername)

    statBox = jmoo_evo(problem, algorithm, configurations, repeat=repeat)
    eval_filename = "./RawData/ExperimentalRecords/" + algorithm.name + "_" + problem.name \
                    + "_" + str(configurations["Universal"]["Population_Size"]) + "_" + str(
        repeat) + ".txt"

    f = open(eval_filename, "w")
    f.write(str(statBox.numEval + configurations["Universal"]["Population_Size"]))
    f.close()
    return eval_filename


class JMOO:
    def __init__(self, tests, reports, configurations):
        self.tests = tests
        self.reports = reports
        self.configurations = configurations

    def doTests(self):
        results = []


        times = {}
        # Main control loop
        pool = mp.Pool()
        for problem in self.tests.problems:
            times[problem.name] = {}
            for algorithm in self.tests.algorithms:
                times[problem.name][algorithm.name] = []
                for repeat in range(self.configurations["Universal"]["Repeats"]):
                    init = time.time()
                    call_jmoo_evo(problem, algorithm, self.configurations, repeat)
                    times[problem.name][algorithm.name].append(time.time() - init)
                    print times
                    # print problem.name, algorithm.name, repeat
                    # pool.apply_async(call_jmoo_evo, (problem, algorithm, self.configurations, repeat))

        pool.close()
        pool.join()
        print(results)
        import pickle
        pickle.dump(times, open('time.p', 'w'))


                    
                    
                    
    def doReports(self,thing=""):
        for report in self.reports:
            report.doit(tagnote=thing)
