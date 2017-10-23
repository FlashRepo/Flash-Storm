"""
This is to generate graphs
"""
from __future__ import division
import pandas as pd
import matplotlib.pyplot as plt

problems = ["POM3A", "POM3B", "POM3C", "POM3D",
            "xomo_flight", "xomo_all", "xomo_ground", "xomo_osp", "xomoo2",
            "MONRP_50_4_5_0_90", "MONRP_50_4_5_0_110", "MONRP_50_4_5_4_90", "MONRP_50_4_5_4_110"
            ]

algorithms = [ "SWAY5", "SPEA2", "NSGAII"]
populations = [100, 512, 1024, 2048, 4096, 8192, 10000]
measures = ['Median-HV', 'Median-spreads']


def process(filename):

    df = pd.read_csv(filename)
    for problem in problems:
        print problem
        for measure in measures:
            fig, ax = plt.subplots()
            problem_df = df[df.Problem == problem]
            problem_df = problem_df.sort('PopSize')
            problem_sway5 = problem_df[problem_df.Algorithm == 'SWAY5']
            problem_spea = problem_df[problem_df.Algorithm == 'SPEA2']
            problem_nsga = problem_df[problem_df.Algorithm == 'NSGAII']
            assert(len(problem_nsga) == 1), "Something is wrong"
            assert(len(problem_spea) == 1), "Something is wrong"
            assert(len(problem_spea) + len(problem_nsga) + len(problem_sway5) == len(problem_df)), "something is wrong"
            pops = problem_sway5['PopSize'].tolist()
            vals = problem_sway5[measure].tolist()
            nsgas = problem_nsga[measure].tolist() * len(pops)
            speas = problem_spea[measure].tolist() * len(pops)
            ax.plot(pops, vals)
            ax.plot(pops, nsgas)
            ax.plot(pops, speas)
            filename = "./Figures/" + problem + "_" + measure + ".png"
            plt.ylabel(measure)
            plt.xlabel("Population Size")
            plt.title(problem + " " + measure)
            plt.savefig(filename)
            plt.cla()





if __name__ == "__main__":
    process("./result.csv")