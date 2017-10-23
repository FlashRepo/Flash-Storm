from __future__ import division
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

"Brief notes"
"Objective Space Plotter"

# from pylab import *

from time import strftime

from pylab import *

from jmoo_properties import *
from utility import *


def read_initial_population(prob, filename):
    fd_initial_data = open(filename, 'rb')
    reader_initial_data = csv.reader(fd_initial_data, delimiter=',')
    initial = []
    row_count = sum(1 for _ in csv.reader(open(filename)))
    for i,row in enumerate(reader_initial_data):
        if i > 1 and i != row_count-1:
                row = map(float, row)
                try: initial.append(prob.evaluate(row)[-1])
                except: pass
    return initial


def joes_diagrams(problems, algorithms, Configurations, tag="JoeDiagram"):
    date_folder_prefix = strftime("%m-%d-%Y")


    base = []
    final = []
    data = []

    for p,prob in enumerate(problems):
        base.append([])
        final.append([])
        data.append([])

        for a,alg in enumerate(algorithms):


            # finput = open("data/" + prob.name + "-p" + str(Configurations["Universal"]["Population_Size"]) + "-d"  + str(len(prob.decisions)) + "-o" + str(len(prob.objectives)) + "-dataset.txt", 'rb')
            f3input = open("data/results_" + prob.name + "-p" + str(Configurations["Universal"]["Population_Size"]) + "-d"  + str(len(prob.decisions)) + "-o" + str(len(prob.objectives)) + "_" + alg.name + ".datatable", 'rb')
            # f4input = open(DATA_PREFIX + "decision_bin_table" + "_" + prob.name+ "-p" + str(Configurations["Universal"]["Population_Size"]) + "-d"  + str(len(prob.decisions)) + "-o" + str(len(prob.objectives))  + "_" + alg.name + DATA_SUFFIX, 'rb')
            # reader = csv.reader(finput, delimiter=',')
            reader3 = csv.reader(f3input, delimiter=',')
            # reader4 = csv.reader(f4input, delimiter=',')
            base[p].append( [] )
            final[p].append( [] )
            data[p].append( [] )

            for i,row in enumerate(reader3):
                if not str(row[0]) == "0":
                    for j,col in enumerate(row):
                        if i == 0:
                            data[p][a].append([])
                        else:
                            if not col == "":
                                data[p][a][j].append(float(col.strip("%)(")))

    colors = ['r', 'b', 'g']
    from matplotlib.font_manager import FontProperties
    font = {'family' : 'sans-serif',
            'weight' : 'normal',
            'size'   : 8}

    matplotlib.rc('font', **font)
    fontP = FontProperties()
    fontP.set_size('x-small')


    codes = ["b*", "r.", "g*"]

    line =  "-"
    dotted= "--"
    algnames = [alg.name for alg in algorithms]
    axy = [0,1,2,3]
    axx = [0,0,0,0]
    codes2= ["b-", "r-", "g-"]
    colors= ["b", "r", "g"]
    ms = 8
    #fig  = plt.figure()
    #ax = fig.gca(projection='3d')




    for p,prob in enumerate(problems):
                f, axarr = plt.subplots(len(prob.objectives))#+1, len(prob.objectives))

                for o, obj in enumerate(prob.objectives):
                    maxEvals = 0
                    for a,alg in enumerate(algorithms):
                        try:
                            maxEvals = max(maxEvals, max(data[p][a][0]))
                        except:
                            pass
                            # import pdb
                            # pdb.set_trace()
                    for a,alg in enumerate(algorithms):

                        scores = {}
                        for score,eval in zip(data[p][a][o*3+2], data[p][a][0]):
                            eval = int(round(eval/5.0)*5.0)
                            if eval in scores: scores[eval].append(score)
                            else: scores[eval] = [score]

                        keylist = [1]
                        scorelist = [100]
                        smallslist = [100]
                        for eval in sorted(scores.keys()):
                            lq = getPercentile(scores[eval], 25)
                            uq = getPercentile(scores[eval], 75)
                            scores[eval] = [score for score in scores[eval] if score >= lq and score <= uq ]
                            for item in scores[eval]:
                                keylist.append(eval)
                                scorelist.append(item)
                                if len(smallslist) == 0:
                                    smallslist.append(min(scores[eval]))
                                else:
                                    smallslist.append(    min(min(scores[eval]), min(smallslist))  )

                        axarr[o].plot(keylist, scorelist, linestyle='None', label=alg.name, marker=alg.type, color=alg.color, markersize=8, markeredgecolor='none')
                        axarr[o].plot(keylist, smallslist, color=alg.color)
                        # axarr[o].set_ylim(0, 130)
                        # axarr[o].set_autoscale_on(True)
                        axarr[o].set_xlim([-10, 10000])
                        axarr[o].set_xscale('log', nonposx='clip')
                        axarr[o].set_ylabel(obj.name)


                if not os.path.isdir('./Results/Charts/' + date_folder_prefix):
                    os.makedirs('./Results/Charts/' + date_folder_prefix)

                f.suptitle(prob.name)
                fignum = len([name for name in os.listdir('./Results/Charts/' + date_folder_prefix)]) + 1
                plt.legend(loc='lower center', bbox_to_anchor=(1, 0.5))
                plt.savefig('./Results/Charts/' + date_folder_prefix + '/figure' + str("%02d" % fignum) + "_" + prob.name + "_" + tag + '.png', dpi=100)
                cla()


def hypervolume_graphs(problems, algorithms, Configurations, aggregate_measure=mean, tag="HyperVolume"):
    def get_data_from_archive(problems, algorithms, Configurations, function):
        from PerformanceMeasures.DataFrame import ProblemFrame
        problem_dict = {}
        for problem in problems:
            data = ProblemFrame(problem, algorithms)
            reference_point = data.get_reference_point(Configurations["Universal"]["No_of_Generations"])
            generation_dict = {}
            for generation in xrange(Configurations["Universal"]["No_of_Generations"]):
                population = data.get_frontier_values(generation)
                evaluations = data.get_evaluation_values(generation)
                algorithm_dict = {}
                for algorithm in algorithms:
                    repeat_dict = {}
                    for repeat in xrange(Configurations["Universal"]["Repeats"]):
                        candidates = [pop.objectives for pop in population[algorithm.name][repeat]]
                        repeat_dict[str(repeat)] = {}
                        if len(candidates) > 0:
                            repeat_dict[str(repeat)]["HyperVolume"] = function(reference_point, candidates)
                            if repeat_dict[str(repeat)]["HyperVolume"] == 0:
                                pass
                            repeat_dict[str(repeat)]["Evaluations"] = evaluations[algorithm.name][repeat]
                        else:
                            repeat_dict[str(repeat)]["HyperVolume"] = None
                            repeat_dict[str(repeat)]["Evaluations"] = None

                    algorithm_dict[algorithm.name] = repeat_dict
                generation_dict[str(generation)] = algorithm_dict
            problem_dict[problem.name] = generation_dict
        return problem_dict

    from PerformanceMetrics.HyperVolume.hv import get_hyper_volume
    result = get_data_from_archive(problems, algorithms, Configurations, get_hyper_volume)
    import pdb
    pdb.set_trace()

    date_folder_prefix = strftime("%m-%d-%Y")

    problem_scores = {}
    for problem in problems:
        f, axarr = plt.subplots(1)
        scores = {}
        for algorithm in algorithms:
            median_scores = []
            median_evals = []
            for generation in xrange(Configurations["Universal"]["No_of_Generations"]):
                temp_result = result[problem.name][str(generation)][algorithm.name]
                hypervolume_list = [temp_result[str(repeat)]["HyperVolume"] for repeat in xrange(Configurations["Universal"]["Repeats"]) if temp_result[str(repeat)]["HyperVolume"] is not None]

                old_evals = [sum([result[problem.name][str(tgen)][algorithm.name][str(repeat)]["Evaluations"] for tgen in xrange(generation) if result[problem.name][str(tgen)][algorithm.name][str(repeat)]["Evaluations"] is not None]) for repeat in xrange(Configurations["Universal"]["Repeats"])]
                evaluation_list = [temp_result[str(repeat)]["Evaluations"] for repeat in xrange(Configurations["Universal"]["Repeats"]) if temp_result[str(repeat)]["Evaluations"] is not None]

                assert(len(hypervolume_list) == len(evaluation_list)), "Something is wrong"
                if len(hypervolume_list) > 0 and len(evaluation_list) > 0:
                    median_scores.append(aggregate_measure(hypervolume_list))
                    median_evals.append(aggregate_measure(old_evals))
                    # if algorithm.name == "SWAY2":
                    #     # print hypervolume_list, aggregate_measure(hypervolume_list)
                    #     # print ">> ", old_evals, aggregate_measure(old_evals)
                    #     print "scores : ", median_scores
                    #     print "evals : ", median_evals



            scores[algorithm.name] = aggregate_measure(median_scores)
            # if algorithm.name == "SWAY2":
            #     print median_evals
            #     print ">> ", median_scores, id(median_scores)
            #     exit()
            axarr.plot(median_evals, median_scores, linestyle='None', label=algorithm.name, marker=algorithm.type, color=algorithm.color, markersize=8, markeredgecolor='none')
            axarr.plot(median_evals, median_scores, color=algorithm.color)
            # axarr[o].set_ylim(0, 130)
            axarr.set_autoscale_on(True)
            axarr.set_xlim([-10, 10000])
            axarr.set_xscale('log', nonposx='clip')
            axarr.set_ylabel("HyperVolume")
        if not os.path.isdir('./Results/Charts/' + date_folder_prefix):
            os.makedirs('./Results/Charts/' + date_folder_prefix)

        f.suptitle(problem.name)
        fignum = len([name for name in os.listdir('./Results/Charts/' + date_folder_prefix)]) + 1
        plt.legend(loc='lower center', bbox_to_anchor=(1, 0.5))
        plt.savefig('./Results/Charts/' + date_folder_prefix + '/figure' + str("%02d" % fignum) + "_" + problem.name + "_" + tag + '.png', dpi=100)
        cla()
        problem_scores[problem.name] = scores

    return problem_scores


def spread_graphs(problems, algorithms, Configurations,aggregate_measure=mean, tag="Spread"):
    def get_data_from_archive(problems, algorithms, Configurations, function):
        from PerformanceMeasures.DataFrame import ProblemFrame
        problem_dict = {}
        for problem in problems:
            print problem.name
            data = ProblemFrame(problem, algorithms)
            extreme_point1, extreme_point2 = data.get_extreme_points(Configurations["Universal"]["Repeats"])
            generation_dict = {}
            for generation in xrange(Configurations["Universal"]["No_of_Generations"]):
                population = data.get_frontier_values(generation)
                evaluations = data.get_evaluation_values(generation)
                algorithm_dict = {}
                for algorithm in algorithms:
                    repeat_dict = {}
                    for repeat in xrange(Configurations["Universal"]["Repeats"]):
                        candidates = [pop.objectives for pop in population[algorithm.name][repeat]]
                        repeat_dict[str(repeat)] = {}
                        if len(candidates) > 0:
                            try:
                                repeat_dict[str(repeat)]["Spread"] = function(candidates, extreme_point1, extreme_point2)
                                repeat_dict[str(repeat)]["Evaluations"] = evaluations[algorithm.name][repeat]
                            except:
                                repeat_dict[str(repeat)]["Spread"] = None
                                repeat_dict[str(repeat)]["Evaluations"] = None
                        else:
                            repeat_dict[str(repeat)]["Spread"] = None
                            repeat_dict[str(repeat)]["Evaluations"] = None
                    algorithm_dict[algorithm.name] = repeat_dict
                generation_dict[str(generation)] = algorithm_dict
            problem_dict[problem.name] = generation_dict
        return problem_dict

    from PerformanceMetrics.Spread.Spread import spread_calculator
    result = get_data_from_archive(problems, algorithms, Configurations, spread_calculator)
    date_folder_prefix = strftime("%m-%d-%Y")


    problem_scores = {}
    for problem in problems:
        f, axarr = plt.subplots(1)
        scores = {}
        for algorithm in algorithms:
            median_scores = []
            median_evals = []
            for generation in xrange(Configurations["Universal"]["No_of_Generations"]):
                temp_result = result[problem.name][str(generation)][algorithm.name]
                hypervolume_list = [temp_result[str(repeat)]["Spread"] for repeat in xrange(Configurations["Universal"]["Repeats"]) if temp_result[str(repeat)]["Spread"] is not None]

                old_evals = [sum([result[problem.name][str(tgen)][algorithm.name][str(repeat)]["Evaluations"] for tgen in xrange(generation) if result[problem.name][str(tgen)][algorithm.name][str(repeat)]["Evaluations"] is not None]) for repeat in xrange(Configurations["Universal"]["Repeats"])]
                evaluation_list = [temp_result[str(repeat)]["Evaluations"] for repeat in xrange(Configurations["Universal"]["Repeats"]) if temp_result[str(repeat)]["Evaluations"] is not None]

                assert(len(hypervolume_list) == len(evaluation_list)), "Something is wrong"
                if len(hypervolume_list) > 0 and len(evaluation_list) > 0:
                    median_scores.append(aggregate_measure(hypervolume_list))
                    median_evals.append(aggregate_measure(old_evals))

            # print "Problem: ", problem.name, " Algorithm: ", algorithm.name, " Mean HyperVolume: ", mean(median_scores)
            scores[algorithm.name] = aggregate_measure(median_scores)
            axarr.plot(median_evals, median_scores, linestyle='None', label=algorithm.name, marker=algorithm.type, color=algorithm.color, markersize=8, markeredgecolor='none')
            axarr.plot(median_evals, median_scores, color=algorithm.color)
            # axarr[o].set_ylim(0, 130)
            axarr.set_autoscale_on(True)
            axarr.set_xlim([-10, 10000])
            axarr.set_xscale('log', nonposx='clip')
            axarr.set_ylabel("Spread")
        if not os.path.isdir('./Results/Charts/' + date_folder_prefix):
            os.makedirs('./Results/Charts/' + date_folder_prefix)

        f.suptitle(problem.name)
        fignum = len([name for name in os.listdir('./Results/Charts/' + date_folder_prefix)]) + 1
        plt.legend(loc='lower center', bbox_to_anchor=(1, 0.5))
        plt.savefig('./Results/Charts/' + date_folder_prefix + '/figure' + str("%02d" % fignum) + "_" + problem.name + "_" + tag + '.png', dpi=100)
        cla()
        problem_scores[problem.name] = scores
    return problem_scores


def statistic_reporter(problems, algorithms, Configurations,aggregate_measure=mean,  tag="RunTimes"):
    def get_filename():
        from time import strftime
        date_folder_prefix = strftime("%m-%d-%Y")
        folder_name = "./RawData/ExperimentalRecords/"
        folder_name = sorted([os.path.join(folder_name,d) for d in os.listdir(folder_name)], key=os.path.getmtime)[-1]
        from os import listdir
        from os.path import isfile, getmtime
        all_files = [folder_name + "/" + d for d in listdir(folder_name) if isfile(folder_name + "/" + d)]
        latest_file = sorted(all_files, key=getmtime)[-1]
        print latest_file
        return latest_file

    def draw(title, y, names, tag=""):
        ind = np.arange(len(y))
        width = 0.5
        figure = plt.figure()
        ax = plt.subplot(111)
        ax.bar(ind, y)
        plt.ylabel(tag)
        plt.title(title)
        plt.xticks(ind + width/2., names)
        date_folder_prefix = strftime("%m-%d-%Y")
        if not os.path.isdir('./Results/Charts/' + date_folder_prefix):
            os.makedirs('./Results/Charts/' + date_folder_prefix)

        fignum = len([name for name in os.listdir('./Results/Charts/' + date_folder_prefix)]) + 1
        plt.savefig('./Results/Charts/' + date_folder_prefix + '/figure' + str("%02d" % fignum) + "_" + problem.name + "_" + tag + '.png', dpi=100)
        cla()


    import xml.etree.ElementTree as ET
    doc = ET.parse(get_filename())
    root = doc.getroot()

    extracted_problems = [child for child in root if child.attrib["name"] in [problem.name for problem in problems]]
    # assert(len(extracted_problems) == len(problem)), "The problems in the experiment have to be run at the same time"

    results = {}
    for extracted_problem in extracted_problems:
        algorithm_result = {}
        for extracted_algorithm in extracted_problem:
            run_result = {}
            for extracted_run in extracted_algorithm:
                per_run_result = {"evaluation": float(extracted_run[0][0].text),
                                  "run_time": float(extracted_run[0][1].text)}
                run_result[extracted_run.attrib["id"]] = per_run_result
            algorithm_result[extracted_algorithm.attrib["name"]] = run_result
        results[extracted_problem.attrib["name"]] = algorithm_result

    for problem in problems:
        algorithm_name = []
        average_runtime = []
        average_evaluation = []
        for a, algorithm in enumerate(algorithms):
            algorithm_name.append(algorithm.name)
            average_runtime.append(aggregate_measure([float(results[problem.name][algorithm.name][str(r+1)]["run_time"]) for r in xrange(Configurations["Universal"]["Repeats"])]))
            average_evaluation.append(aggregate_measure([float(results[problem.name][algorithm.name][str(r+1)]["evaluation"]) for r in xrange(Configurations["Universal"]["Repeats"])]))

        draw(problem.name, average_runtime, algorithm_name, "Runtimes")
        draw(problem.name, average_evaluation, algorithm_name, "Evaluations")


def comparision_reporter(problems, algorithms, list_hypervolume_scores, list_spread_scores, list_igd_scores, base_line, tag="Comparisions"):
    # TODO: write comment

    for measure_name, list_xx_scores in zip(["HyperVolume", "Spread", "IGD"], [list_hypervolume_scores, list_spread_scores, list_igd_scores]):

        print measure_name
        print list_xx_scores
        print "---" * 20

        # concatenating the dictionaries
        x_scores = list_xx_scores[0]
        for x_score in list_xx_scores: x_scores.update(x_score)
        x_dpoints = []
        for problem in problems:
            base_score = float(x_scores[problem.name][base_line])
            for algorithm in algorithms:
                print measure_name, problem.name, algorithm.name, x_scores[problem.name][algorithm.name]/base_score

                temp_score = (x_scores[problem.name][algorithm.name]/base_score) * 100
                x_dpoints.append([algorithm.name, problem.name, temp_score])

        np_x_dpoints = np.array(x_dpoints)

        date_folder_prefix = strftime("%m-%d-%Y")
        if not os.path.isdir('./Results/Charts/' + date_folder_prefix):
                os.makedirs('./Results/Charts/' + date_folder_prefix)
        fignum = len([name for name in os.listdir('./Results/Charts/' + date_folder_prefix)]) + 1
        file_name = './Results/Charts/' + date_folder_prefix + '/figure' + str("%02d" % fignum) + "_" + tag + measure_name + '.png'

        from Graphs.grouped_bar_plots import barplot
        barplot(np_x_dpoints, file_name, tag + measure_name, {alg.name:alg.color for alg in algorithms})


def igd_reporter(problems, algorithms, Configurations, aggregate_measure=mean, tag="IGD"):
    def get_data_from_archive(problems, algorithms, Configurations, function):
        from PerformanceMeasures.DataFrame import ProblemFrame
        problem_dict = {}
        for problem in problems:
            data = ProblemFrame(problem, algorithms)

            # # finding the final frontier
            final_frontiers = data.get_frontier_values()

            # unpacking the final frontiers
            unpacked_frontier = []
            for key in final_frontiers.keys():
                for repeat in final_frontiers[key]:
                    unpacked_frontier.extend(repeat)


            # Vivek: I have noticed that some of the algorithms (specifically VALE8) produces duplicate points
            # which would then show up in nondominated sort and tip the scale in its favour. So I would like to remove
            # all the duplicate points from the population and then perform a non dominated sort
            old = len(unpacked_frontier)
            unpacked_frontier = list(set(unpacked_frontier))
            if len(unpacked_frontier) - old == 0:
                print "There are no duplicates!! check"

            # Find the non dominated solutions

            # change into jmoo_individual
            from jmoo_individual import jmoo_individual
            population = [jmoo_individual(problem, i.decisions, i.objectives) for i in unpacked_frontier]

            # Vivek: I first tried to choose only the non dominated solutions. But then there are only few solutions
            # (in order of 1-2) so I am just doing a non dominated sorting with crowd distance
            actual_frontier = [sol.fitness.fitness for sol in get_non_dominated_solutions(problem, population, Configurations)]
            assert(len(actual_frontier) == Configurations["Universal"]["Population_Size"])


            generation_dict = {}
            for generation in xrange(Configurations["Universal"]["No_of_Generations"]):
                #
                population = data.get_frontier_values(generation)
                evaluations = data.get_evaluation_values(generation)

                algorithm_dict = {}
                for algorithm in algorithms:
                    repeat_dict = {}
                    for repeat in xrange(Configurations["Universal"]["Repeats"]):
                        candidates = [pop.objectives for pop in population[algorithm.name][repeat]]
                        repeat_dict[str(repeat)] = {}
                        from PerformanceMetrics.IGD.IGD_Calculation import IGD
                        if len(candidates) > 0:
                            repeat_dict[str(repeat)]["IGD"] = IGD(actual_frontier, candidates)
                            repeat_dict[str(repeat)]["Evaluations"] = evaluations[algorithm.name][repeat]
                        else:
                            repeat_dict[str(repeat)]["IGD"] = None
                            repeat_dict[str(repeat)]["Evaluations"] = None

                    algorithm_dict[algorithm.name] = repeat_dict
                generation_dict[str(generation)] = algorithm_dict
            problem_dict[problem.name] = generation_dict
        return problem_dict, actual_frontier

    from PerformanceMetrics.HyperVolume.hv import get_hyper_volume
    result, actual_frontier = get_data_from_archive(problems, algorithms, Configurations, get_hyper_volume)

    date_folder_prefix = strftime("%m-%d-%Y")
    if not os.path.isdir('./Results/Final_Frontier/' + date_folder_prefix):
            os.makedirs('./Results/Final_Frontier/' + date_folder_prefix)

    date_folder_prefix = strftime("%m-%d-%Y")
    if not os.path.isdir('./Results/Charts/' + date_folder_prefix):
            os.makedirs('./Results/Charts/' + date_folder_prefix)

    problem_scores = {}
    for problem in problems:
        print problem.name
        from PerformanceMetrics.IGD.IGD_Calculation import IGD
        baseline_igd = IGD(actual_frontier, baseline_objectives(problem, Configurations))

        # write the final frontier
        fignum = len([name for name in os.listdir('./Results/Final_Frontier/' + date_folder_prefix)]) + 1
        filename_frontier = './Results/Final_Frontier/' + date_folder_prefix + '/table' + str("%02d" % fignum) + "_" \
                             + problem.name + "_" + tag + '.csv'
        ffrontier = open(filename_frontier, "w")
        for l in actual_frontier:
            string_l = ",".join(map(str, l))
            ffrontier.write(string_l + "\n")
        ffrontier.close()

        f, axarr = plt.subplots(1)
        scores = {}
        for algorithm in algorithms:
            median_scores = []
            median_evals = []
            Tables_Content = ""
            Tables_Content += "Generation, o25, o50, o75, n25, n50, n75 \n"

            for generation in xrange(Configurations["Universal"]["No_of_Generations"]):
                temp_result = result[problem.name][str(generation)][algorithm.name]
                hypervolume_list = [temp_result[str(repeat)]["IGD"] for repeat in xrange(Configurations["Universal"]["Repeats"]) if temp_result[str(repeat)]["IGD"] is not None]

                old_evals = [sum([result[problem.name][str(tgen)][algorithm.name][str(repeat)]["Evaluations"] for tgen in xrange(generation) if result[problem.name][str(tgen)][algorithm.name][str(repeat)]["Evaluations"] is not None]) for repeat in xrange(Configurations["Universal"]["Repeats"])]
                evaluation_list = [temp_result[str(repeat)]["Evaluations"] for repeat in xrange(Configurations["Universal"]["Repeats"]) if temp_result[str(repeat)]["Evaluations"] is not None]

                assert(len(hypervolume_list) == len(evaluation_list)), "Something is wrong"
                if len(hypervolume_list) > 0 and len(evaluation_list) > 0:
                    o25 = getPercentile(hypervolume_list, 25)
                    o50 = getPercentile(hypervolume_list, 50)
                    o75 = getPercentile(hypervolume_list, 75)
                    Tables_Content += str(generation) + "," + str(o25) + "," + str(o50) + "," + str(o75) + "," + str(
                        (o25 - baseline_igd) / baseline_igd) + "," + str(
                        (o50 - baseline_igd) / baseline_igd) + "," + str((o75 - baseline_igd) / baseline_igd) + "\n"
                    median_scores.append(aggregate_measure(hypervolume_list))
                    median_evals.append(aggregate_measure(old_evals))

            if not os.path.isdir('./Results/Tables/' + date_folder_prefix):
                    os.makedirs('./Results/Tables/' + date_folder_prefix)
            fignum = len([name for name in os.listdir('./Results/Tables/' + date_folder_prefix)]) + 1
            filename_table = './Results/Tables/' + date_folder_prefix + '/table' + str("%02d" % fignum) + "_" \
                             + algorithm.name + "_" + problem.name + "_" + tag + '.csv'

            # print Tables_Content
            open(filename_table, "w").write(Tables_Content)

            scores[algorithm.name] = aggregate_measure(median_scores)
            axarr.plot(median_evals, median_scores, linestyle='None', label=algorithm.name, marker=algorithm.type, color=algorithm.color, markersize=8, markeredgecolor='none')
            axarr.plot(median_evals, median_scores, color=algorithm.color)
            # axarr[o].set_ylim(0, 130)
            axarr.set_autoscale_on(True)
            axarr.set_xlim([-10, 10000])
            axarr.set_xscale('log', nonposx='clip')
            axarr.set_ylabel("IGD")


        f.suptitle(problem.name)
        fignum = len([name for name in os.listdir('./Results/Charts/' + date_folder_prefix)]) + 1
        plt.legend(loc='lower center', bbox_to_anchor=(1, 0.5))
        plt.savefig('./Results/Charts/' + date_folder_prefix + '/figure' + str("%02d" % fignum) + "_" + problem.name + "_" + tag + '.png', dpi=100)
        cla()
        problem_scores[problem.name] = scores

    return problem_scores


def baseline_objectives(prob, Configurations):
    file_handle = open("data/" + prob.name + "-p" + str(Configurations["Universal"]["Population_Size"]) + "-d"  + str(len(prob.decisions)) + "-o" + str(len(prob.objectives)) + "-dataset.txt", 'rb')
    objectives = []
    for i, line in enumerate(file_handle):
        if i != 0 and i <= Configurations["Universal"]["Population_Size"]: objectives.append(map(float, line.strip().split(","))[-1*len(prob.objectives):])
    return objectives


def hypervolume_approximate_ranking(problems, algorithms, Configurations, tag="hv_approx"):
    def get_data_from_archive(problems, algorithms, Configurations):
        from PerformanceMeasures.DataFrame import ProblemFrame
        problem_dict = {}
        for problem in problems:
            data = ProblemFrame(problem, algorithms)
            generation_dict = {}
            for generation in xrange(Configurations["Universal"]["No_of_Generations"]):
                population = data.get_frontier_values(generation)
                evaluations = data.get_evaluation_values(generation)

                repeat_dict = {}
                for repeat in xrange(Configurations["Universal"]["Repeats"]):
                    algorithm_dict = {}
                    for algorithm in algorithms:
                        algorithm_dict[algorithm.name] ={}
                        try:
                            candidates = [jmoo_individual(problem, pop.decisions, pop.objectives) for pop in
                                          population[algorithm.name][repeat]]
                        except:
                            import pdb
                            pdb.set_trace()
                        repeat_dict[str(repeat)] = {}
                        if len(candidates) > 0:
                            algorithm_dict[algorithm.name]["Solutions"] = candidates
                            algorithm_dict[algorithm.name]["Evaluations"] = evaluations[algorithm.name][repeat]
                        else:
                            algorithm_dict[algorithm.name]["Solutions"] = None
                            algorithm_dict[algorithm.name]["Evaluations"] = None

                    repeat_dict[str(repeat)] = algorithm_dict
                generation_dict[str(generation)] = repeat_dict
            problem_dict[problem.name] = generation_dict
        return problem_dict


    date_folder_prefix = strftime("%m-%d-%Y")
    if not os.path.isdir('./Results/Approx_HyperVolume/' + date_folder_prefix):
            os.makedirs('./Results/Approx_HyperVolume/' + date_folder_prefix)

    result = get_data_from_archive(problems, algorithms, Configurations)
    for problem in problems:
        print ".",
        import sys
        sys.stdout.flush()
        from PerformanceMetrics.HyperVolumeEstimator.hypervolume_estimator import hypervolume_ranking
        ranking_string = hypervolume_ranking(problem, result[problem.name])

        # write the final frontier
        fignum = len([name for name in os.listdir('./Results/Approx_HyperVolume/' + date_folder_prefix)]) + 1
        filename_frontier = './Results/Approx_HyperVolume/' + date_folder_prefix + '/table' + str("%02d" % fignum) + "_" \
                             + problem.name + "_" + tag + '.csv'
        hv_approx = open(filename_frontier, "w")
        hv_approx.write(ranking_string)
        hv_approx.close()


def charter_reporter(problems, algorithms, Configurations, tag=""):
    import sys
    sys.setrecursionlimit(10000)
    hypervolume_scores = hypervolume_graphs(problems, algorithms, Configurations, aggregate_measure=median)
    spread_scores = spread_graphs(problems, algorithms, Configurations, aggregate_measure=median)
    # joes_diagrams(problems, algorithms, Configurations)
    igd_scores = igd_reporter(problems, algorithms, Configurations)
    # hypervolume_approximate_ranking(problems, algorithms, Configurations)
    return [hypervolume_scores, spread_scores, igd_scores]



