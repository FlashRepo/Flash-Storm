from __future__ import division

from random import uniform

###### something you might want to modify to fit your own code #######


def Better(a, b):
    "definition of Better"
    return a < b


def getobj(a):
    "get objective value of candidate; returns a list"
    return a.getobj()


def better(problem, individual, mutant):

    assert (len(individual) == len(mutant)), "Length of mutant and parent should be the same"
    conditions = [i<m for i, m in zip(individual, mutant)]
    if reduce(lambda x, y: x and y, conditions) : return True
    else: return False


def inbox(problem, pebble, frontier):
    "is the peddle inside the hyper volume"
    for candidate in frontier:
        if better(problem, candidate.fitness.fitness, pebble):
            return True
    return False


def hve(problem, frontier, min, max, sample=10000):
    "estimate hyper volumn of frontier"
    count = 0
    m = len(frontier[0].fitness.fitness)
    for i in xrange(sample):
        pebble = [uniform(min[k], max[k]) for k in xrange(m)]
        if inbox(problem, pebble, frontier):count += 1
    return count / (sample)


def hypervolume_ranking(problem, raw_scores):
    """
    This function would return the ranked list of the algorithm based on hypervolume. 1- means highest hypervolume
    :param problem: instance of jmoo_problem
    :param scores: dictionary with algorithm as keys and list of list (objectives)
    :return: ranked list
    """
    def find_utopia(dict_solutions):
        """solution is a dictionary"""
        objectives = len(problem.objectives)
        solutions = [sol.fitness.fitness for sol in dict_solutions["Solutions"]]
        return [min(sol[o] for sol in solutions) * 0.9 for o in xrange(objectives)]

    def find_nadir(dict_solutions):
        objectives = len(problem.objectives)
        solutions = [sol.fitness.fitness for sol in dict_solutions["Solutions"]]
        return [max(sol[o] for sol in solutions) * 1.5 for o in xrange(objectives)]

    generations = [str(s) for s in sorted(map(int, raw_scores.keys()))]

    string_generation = ""
    for generation in generations:
        print "#",
        import sys
        sys.stdout.flush()
        repeats = [str(s) for s in sorted(map(int, raw_scores[generation].keys()))]
        repeat_results = []
        for repeat in repeats:

            algorithms = raw_scores[generation][repeat]
            results = []
            for algorithm in algorithms:
                scores = raw_scores[generation][repeat]
                if scores[algorithm]["Solutions"] is not None:
                    hypervolume = hve(problem, scores[algorithm]["Solutions"], find_utopia(scores[algorithm]), find_nadir(scores[algorithm]))
                    results.append([algorithm, hypervolume])
                else: results.append([algorithm, 0])  # 0 is the worst possible value
            repeat_results.append([l[0] for l in sorted(results, key=lambda x:x[1], reverse=True)])

        # final ranking
        ranking_dict = {}
        for r_r in repeat_results:
            for i, alg in enumerate(r_r):
                if alg in ranking_dict.keys(): ranking_dict[alg] += i
                else: ranking_dict[alg] = i

        import operator
        string_generation += ",".join([a[0] for a in sorted(ranking_dict.items(), key=operator.itemgetter(1))]) + "\n"

    return string_generation

