from __future__ import division
import matplotlib.pyplot as plt


normalization = []


def find_files(problem, algorithm, rep, gen, population):
    sep = "_"
    main_file_path = "./RawData/PopulationArchives/"
    problem_algorithm_path = main_file_path + algorithm + sep + problem + "_" + str(population) + "/"
    rep_path = problem_algorithm_path + str(rep) + "/"
    gen_path = rep_path + str(gen) + ".txt"
    return gen_path


def find_files_for_generations(problem, algorithm, number_of_repeats, gen, pop_no):
    name = problem[-1].name
    return [find_files(name, algorithm, rep_no, gen, pop_no) for rep_no in xrange(number_of_repeats)]


def get_actual_frontier_files(problem, algorithms, max_repeats, max_gens, pop_size):
    files = []
    for algorithm in algorithms:
            files.extend(find_files_for_generations(problem, algorithm.name, max_repeats, max_gens, pop_size))
    return files


def get_content(problem, file, population_size, initial_line=False):
    number_of_objectives = len(problem.objectives)
    objectives = []
    contents = open(file, "r").readlines()
    if initial_line is False:
        for content in contents[:population_size]:
            objectives.append([float(c) for count,c in enumerate(content.split(","))][-1 * number_of_objectives:])
    else:
        for content in contents[1:population_size+1]:
            objectives.append([float(c) for c in content.split(",")][-1 * number_of_objectives:])

    return objectives


def get_content_all(problem, file, population_size, initial_line=True):
    objectives = []
    contents = open(file, "r").readlines()
    if initial_line is True:
        for content in contents[1:population_size+1]:
            temp = [float(c) for c in content.split(",")]
            objectives.append(temp)
    else:
        for content in contents[:population_size]:
            temp = [float(c) for c in content.split(",")]
            objectives.append(temp)
    return objectives

def remove_duplicates(objectives):
    # remove duplicates
    import itertools
    objectives.sort()
    removed = list(objectives for objectives, _ in itertools.groupby(objectives))
    return removed


def get_actual_frontier(problem, algorithms, Configurations, tag):
    number_of_objectives = len(problem[-1].objectives)
    pop_size = Configurations["Universal"]["Population_Size"]
    max_repeats = Configurations["Universal"]["Repeats"]
    max_gens = Configurations["Universal"]["No_of_Generations"]
    files = get_actual_frontier_files(problem, algorithms, max_repeats, max_gens, pop_size)
    content = []
    for file in files:
        content.extend(remove_duplicates(get_content_all(problem[-1], file, pop_size)))

    # change into jmoo_individual
    from jmoo_individual import jmoo_individual
    population = [jmoo_individual(problem[-1], i[number_of_objectives:], i[:number_of_objectives]) for i in content]

    from jmoo_algorithms import get_non_dominated_solutions
    actual_frontier = [sol.fitness.fitness for sol in
                       get_non_dominated_solutions(problem[-1], population, Configurations)]
    return actual_frontier


def get_normalization_values(problem,  gtechnique, Configurations):
    folder_name = "./Data/"
    filename = folder_name + problem.name + "-p" + str(
        Configurations["Universal"]["Population_Size"]) + "-d" + str(len(problem.decisions)) + "-o" + str(
        len(problem.objectives)) + "-g" + gtechnique.__name__ + "-dataset.txt"

    global normalization
    number_of_objectives = len(problem.objectives)
    contents = open(filename, "r").readlines()
    normalization = [map(float, c.split(',')) for c in contents[-1*number_of_objectives:]]


def get_initial_datapoints(problem, algorithm, Configurations):
    number_of_objectives = len(problem.objectives)
    pop_size = Configurations["Universal"]["Population_Size"]
    folder_name = "./Data/"
    sep = "_"
    filename = folder_name + problem.name + "-p" + str(
        Configurations["Universal"]["Population_Size"]) + "-d" + str(len(problem.decisions)) + "-o" + str(
        len(problem.objectives)) + "-dataset.txt"
    content = get_content(problem, filename, pop_size, initial_line=True)
    return content


    # content = get_content_all(problem, filename, pop_size)

    # # change into jmoo_individual
    # from jmoo_individual import jmoo_individual
    # population = [jmoo_individual(problem, i[number_of_objectives:], i[:number_of_objectives]) for i in content]
    #
    # from jmoo_algorithms import get_non_dominated_solutions
    # actual_frontier = [sol.fitness.fitness for sol in
    #                    get_non_dominated_solutions(problem, population, Configurations)]
    # return actual_frontier


def apply_normalization(problem, points):
    norm_points = [[0 for _ in xrange(len(problem.objectives))] for _ in xrange(len(points))]
    for i, point in enumerate(points):
        for objective in xrange(len(problem.objectives)):
            norm_points[i][objective] = (point[objective] - normalization[objective][0])/(normalization[objective][2] - normalization[objective][0])
    return norm_points


def draw_igd(problem, algorithms, gtechniques, Configurations, tag):
    import os
    from time import strftime
    date_folder_prefix = strftime("%m-%d-%Y")
    if not os.path.isdir('./Results/Charts/' + date_folder_prefix):
        os.makedirs('./Results/Charts/' + date_folder_prefix)

    actual_frontier = get_actual_frontier(problem, algorithms, gtechniques, Configurations, tag)
    # actual_frontier = apply_normalization(problem[-1], actual_frontier)
    results = {}
    number_of_repeats = Configurations["Universal"]["Repeats"]
    number_of_objectives = len(problem[-1].objectives)
    generations = Configurations["Universal"]["No_of_Generations"]
    pop_size = Configurations["Universal"]["Population_Size"]
    evaluations = [pop_size*i for i in xrange(generations+1)]

    f, axarr = plt.subplots(1)

    for algorithm in algorithms:
        results[algorithm.name] = {}
        for gtechnique in gtechniques:
            results[algorithm.name][gtechnique.__name__] = []
    for algorithm in algorithms:
        for gtechnique in gtechniques:

            points = get_initial_datapoints(problem[-1], algorithm, gtechnique, Configurations)
            from PerformanceMetrics.IGD.IGD_Calculation import IGD
            results[algorithm.name][gtechnique.__name__].append(IGD(actual_frontier, points))

            for generation in xrange(generations):
                print ".",
                import sys
                sys.stdout.flush()
                temp_igd_list = []
                files = find_files_for_generations(problem[-1].name, algorithm.name, gtechnique.__name__, number_of_repeats, generation+1)
                for file in files:
                    temp_value = get_content_all(problem[-1], file, pop_size, initial_line=False)
                    # change into jmoo_individual
                    from jmoo_individual import jmoo_individual
                    population = [jmoo_individual(problem[-1], i[number_of_objectives:], i[:number_of_objectives]) for i in temp_value]

                    from jmoo_algorithms import get_non_dominated_solutions
                    temp_value = [sol.fitness.fitness for sol in
                                   get_non_dominated_solutions(problem[-1], population, Configurations)]
                    temp_igd_list.append(IGD(actual_frontier, temp_value))
                from numpy import mean
                results[algorithm.name][gtechnique.__name__].append(mean(temp_igd_list))


            if gtechnique.__name__ == "sway":
                lstyle = "--"
                mk = "v"
                ms = 4
            elif gtechnique.__name__ == "wierd":
                lstyle = "-"
                mk = "o"
                ms = 4
            else:
                lstyle = '-'
                mk = algorithm.type
                ms = 8

            axarr.plot(evaluations, results[algorithm.name][gtechnique.__name__], linestyle=lstyle,
               label=algorithm.name + "_" + gtechnique.__name__, marker=mk,
               color=algorithm.color, markersize=ms, markeredgecolor='none')
            axarr.set_autoscale_on(True)
            axarr.set_xlim([0, 10000])
            # axarr.set_xscale('log', nonposx='clip')
            axarr.set_yscale('log', nonposx='clip')
            axarr.set_ylabel("IGD")

            print
            print problem[-1].name, algorithm.name, gtechnique.__name__ , #results[algorithm.name][gtechnique.__name__]

    f.suptitle(problem[-1].name)
    fignum = len([name for name in os.listdir('./Results/Charts/' + date_folder_prefix)]) + 1
    plt.legend(frameon=False, loc='lower center', bbox_to_anchor=(0.5, -0.025), fancybox=True, ncol=2)
    plt.savefig('./Results/Charts/' + date_folder_prefix + '/figure' + str(
    "%02d" % fignum) + "_" + problem[-1].name + "_" + tag + '.png', dpi=100,bbox_inches='tight')
    plt.cla()
    print "Processed: ", problem[-1].name
    import pdb
    pdb.set_trace()


def draw_gd(problem, algorithms, gtechniques, Configurations, tag):
    import os
    from time import strftime
    date_folder_prefix = strftime("%m-%d-%Y")
    if not os.path.isdir('./Results/Charts/' + date_folder_prefix):
        os.makedirs('./Results/Charts/' + date_folder_prefix)

    actual_frontier = get_actual_frontier(problem, algorithms, gtechniques, Configurations, tag)
    # actual_frontier = apply_normalization(problem[-1], actual_frontier)
    results = {}
    number_of_repeats = Configurations["Universal"]["Repeats"]
    number_of_objectives = len(problem[-1].objectives)
    generations = Configurations["Universal"]["No_of_Generations"]
    pop_size = Configurations["Universal"]["Population_Size"]
    evaluations = [pop_size*i for i in xrange(generations+1)]

    f, axarr = plt.subplots(1)

    for algorithm in algorithms:
        results[algorithm.name] = {}
        for gtechnique in gtechniques:
            results[algorithm.name][gtechnique.__name__] = []
    for algorithm in algorithms:
        for gtechnique in gtechniques:

            points = get_initial_datapoints(problem[-1], algorithm, gtechnique, Configurations)
            from PerformanceMetrics.GD.GD_Calculation import GD
            results[algorithm.name][gtechnique.__name__].append(GD(actual_frontier, points))

            for generation in xrange(generations):
                print ".",
                import sys
                sys.stdout.flush()
                temp_gd_list = []
                files = find_files_for_generations(problem[-1].name, algorithm.name, gtechnique.__name__, number_of_repeats, generation+1)
                for file in files:
                    temp_value = get_content_all(problem[-1], file, pop_size, initial_line=False)
                    # change into jmoo_individual
                    from jmoo_individual import jmoo_individual
                    population = [jmoo_individual(problem[-1], i[number_of_objectives:], i[:number_of_objectives]) for i in temp_value]

                    from jmoo_algorithms import get_non_dominated_solutions
                    temp_value = [sol.fitness.fitness for sol in
                                   get_non_dominated_solutions(problem[-1], population, Configurations)]
                    temp_gd_list.append(GD(actual_frontier, temp_value))
                from numpy import mean
                results[algorithm.name][gtechnique.__name__].append(mean(temp_igd_list))


            if gtechnique.__name__ == "sway":
                lstyle = "--"
                mk = "v"
                ms = 4
            elif gtechnique.__name__ == "wierd":
                lstyle = "-"
                mk = "o"
                ms = 4
            else:
                lstyle = '-'
                mk = algorithm.type
                ms = 8

            axarr.plot(evaluations, results[algorithm.name][gtechnique.__name__], linestyle=lstyle,
               label=algorithm.name + "_" + gtechnique.__name__, marker=mk,
               color=algorithm.color, markersize=ms, markeredgecolor='none')
            axarr.set_autoscale_on(True)
            axarr.set_xlim([0, 10000])
            # axarr.set_xscale('log', nonposx='clip')
            axarr.set_yscale('log', nonposx='clip')
            axarr.set_ylabel("GD")

            print
            print problem[-1].name, algorithm.name, gtechnique.__name__ , #results[algorithm.name][gtechnique.__name__]

    f.suptitle(problem[-1].name)
    fignum = len([name for name in os.listdir('./Results/Charts/' + date_folder_prefix)]) + 1
    plt.legend(frameon=False, loc='lower center', bbox_to_anchor=(0.5, -0.025), fancybox=True, ncol=2)
    plt.savefig('./Results/Charts/' + date_folder_prefix + '/figure' + str(
    "%02d" % fignum) + "_" + problem[-1].name + "_" + tag + '.png', dpi=100,bbox_inches='tight')
    plt.cla()
    print "Processed: ", problem[-1].name


def draw_hv(problem, algorithms, Configurations, tag):
    import os
    from time import strftime
    date_folder_prefix = strftime("%m-%d-%Y")
    if not os.path.isdir('./Results/Charts/' + date_folder_prefix):
        os.makedirs('./Results/Charts/' + date_folder_prefix)

    reference_point = [110 for _ in xrange(len(problem[-1].objectives))]
    results = {}
    number_of_repeats = Configurations["Universal"]["Repeats"]
    generations = Configurations["Universal"]["No_of_Generations"]
    pop_size = Configurations["Universal"]["Population_Size"]
    evaluations = [pop_size*i for i in xrange(generations+1)]

    f, axarr = plt.subplots(1)

    # For Normalization
    gtechniques = ["normal"]
    for_normalizing_points = []
    for algorithm in algorithms:
        for gtechnique in gtechniques:
            points = get_initial_datapoints(problem[-1], algorithm, Configurations)
            for_normalizing_points.extend(points)
            print "generation",
            for generation in [0]:
                print generation,
                files = find_files_for_generations(problem, algorithm.name, number_of_repeats, generation + 1, pop_size)
                for file in files:
                    for_normalizing_points.extend(get_content(problem[-1], file, pop_size))

    max_values = []
    min_values = []
    for objx in xrange(len(problem[-1].objectives)):
        temp_values = [fnp[objx] for fnp in for_normalizing_points]
        max_values.append(max(temp_values))
        min_values.append(min(temp_values))
    assert(len(max_values) == len(min_values)), "something is wrong"

    for algorithm in algorithms:
        results[algorithm.name] = {}
        for gtechnique in gtechniques:
            results[algorithm.name][gtechnique] = []

    for algorithm in algorithms:
        for gtechnique in gtechniques:
            raw_points = get_initial_datapoints(problem[-1], algorithm, Configurations)
            points = []
            # Normalize the points
            for rpoint in raw_points:
                temp_rpoint = []
                for objx in xrange(len(problem[-1].objectives)):
                    temp_rpoint.append(((rpoint[objx] - min_values[objx])/(max_values[objx] - min_values[objx]))*100)
                    assert(0 <= temp_rpoint[-1] <= 100), "Something is wrong"
                points.append(temp_rpoint)

            from PerformanceMetrics.HyperVolume.hv import get_hyper_volume
            temp_hv = get_hyper_volume(reference_point, points)

            results[algorithm.name][gtechnique].append(temp_hv)

            for generation in [0]:
                temp_igd_list = []
                files = find_files_for_generations(problem, algorithm.name, number_of_repeats, generation+1, pop_size)
                for file in files:
                    temp_value = get_content(problem[-1], file, pop_size)

                    points = []
                    # Normalize the points
                    for rpoint in temp_value:
                        temp_rpoint = []
                        for objx in xrange(len(problem[-1].objectives)):
                            temp_rpoint.append(
                                ((rpoint[objx] - min_values[objx]) / (max_values[objx] - min_values[objx])) * 100)
                            assert (0 <= temp_rpoint[-1] <= 100), "Something is wrong"
                        points.append(temp_rpoint)

                    temp_hv = get_hyper_volume(reference_point, points)
                    temp_igd_list.append(temp_hv)

                results[algorithm.name][gtechnique].append(temp_igd_list)
    # from numpy import mean
    # print '{0:.10f}'.format((mean(results["SWAY5"]["normal"][-1])))
    print results[algorithm.name][gtechnique][-1], "Algorithm: ", algorithm.name


def find_extreme_points(problem, points):
    from Techniques.euclidean_distance import euclidean_distance
    distance_matrix = [[-1 for _ in xrange(len(points))] for _ in xrange(len(points))]
    for i in xrange(len(points)):
        for j in xrange(len(points)):
            if distance_matrix[i][j] == -1:
                temp_dist = euclidean_distance(points[i], points[j])
                distance_matrix[i][j] = temp_dist
                distance_matrix[j][i] = temp_dist
    max_distance = max([max(maps_objective) for maps_objective in distance_matrix])
    indexes = [[(i, j) for j, distance in enumerate(distances) if distance == max_distance] for i, distances in
               enumerate(distance_matrix)]
    index = [index for index in indexes if len(index) > 0][-1][-1]
    return points[index[0]], points[index[1]]


def draw_spread(problem, algorithms, Configurations, tag):
    import os
    from time import strftime
    number_of_repeats = Configurations["Universal"]["Repeats"]
    pop_size = Configurations["Universal"]["Population_Size"]
    date_folder_prefix = strftime("%m-%d-%Y")
    if not os.path.isdir('./Results/Charts/' + date_folder_prefix):
        os.makedirs('./Results/Charts/' + date_folder_prefix)

    actual_frontier = get_actual_frontier(problem, algorithms, Configurations, tag)
    extreme_point1, extreme_point2 = find_extreme_points(problem[-1], actual_frontier)

    results = {}
    gtechniques = ["normal"]

    for_normalizing_points = []
    for algorithm in algorithms:
        for gtechnique in gtechniques:
            points = get_initial_datapoints(problem[-1], algorithm, Configurations)
            for_normalizing_points.extend(points)
            print "generation",
            for generation in [0]:
                print generation,
                files = find_files_for_generations(problem, algorithm.name, number_of_repeats, generation + 1, pop_size)
                for file in files:
                    for_normalizing_points.extend(get_content(problem[-1], file, pop_size))

    max_values = []
    min_values = []
    for objx in xrange(len(problem[-1].objectives)):
        temp_values = [fnp[objx] for fnp in for_normalizing_points]
        max_values.append(max(temp_values))
        min_values.append(min(temp_values))
    assert (len(max_values) == len(min_values)), "something is wrong"

    for algorithm in algorithms:
        results[algorithm.name] = {}
        for gtechnique in gtechniques:
            results[algorithm.name][gtechnique] = []

    for algorithm in algorithms:
        for gtechnique in gtechniques:

            raw_points = get_initial_datapoints(problem[-1], algorithm, Configurations)
            points = []
            # Normalize the points
            for rpoint in raw_points:
                temp_rpoint = []
                for objx in xrange(len(problem[-1].objectives)):
                    temp_rpoint.append(
                        ((rpoint[objx] - min_values[objx]) / (max_values[objx] - min_values[objx])) * 100)
                    assert (0 <= temp_rpoint[-1] <= 100), "Something is wrong"
                points.append(temp_rpoint)

            from PerformanceMetrics.Spread.Spread import spread_calculator
            temp_spread = spread_calculator(points, extreme_point1,extreme_point2)

            results[algorithm.name][gtechnique].append(temp_spread)


            for generation in [0]:
                print ".",
                temp_igd_list = []
                files = find_files_for_generations(problem, algorithm.name, number_of_repeats, generation+1, Configurations['Universal']['Population_Size'])
                for file in files:
                    temp_value = get_content(problem[-1], file, pop_size)
                    points = []
                    # Normalize the points
                    for rpoint in temp_value:
                        temp_rpoint = []
                        for objx in xrange(len(problem[-1].objectives)):
                            temp_rpoint.append(
                                ((rpoint[objx] - min_values[objx]) / (max_values[objx] - min_values[objx])) * 100)
                            assert (0 <= temp_rpoint[-1] <= 100), "Something is wrong"
                        points.append(temp_rpoint)

                    temp_spread = spread_calculator(points, extreme_point1, extreme_point2)
                    # print [[round(tt, 2) for tt in t] for t in temp_value]
                    temp_igd_list.append(temp_spread)
                from numpy import mean
                results[algorithm.name][gtechnique].append(temp_igd_list)

        print results[algorithm.name][gtechnique][-1], "Algorithm: ", algorithm.name