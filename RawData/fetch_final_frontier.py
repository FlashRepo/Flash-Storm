import sys
import os

folder = "./PopulationArchives/"
subfolders = [folder + sub + "/" for sub in os.listdir(folder) if ".DS_Store" not in sub]
for subfolder in subfolders:
    sub = subfolder.split('/')[-2]
    algorithm = sub.split("_")[0]
    problem = sub.split("_")[1]
    population = sub.split("_")[2]

    repeat_folders = [subfolder + r + "/" for r in os.listdir(subfolder)]
    for repeat_folder in repeat_folders:
        repeat = repeat_folder.split("/")[-2]

        if algorithm == "NSGAII" or algorithm == "SPEA2":
            final_frontier_file = "20.txt"

        final_frontier_file = repeat_folder + final_frontier_file

        # Extract only the objective values
        if "POM" in problem:
            no_objectives = 3
        elif "xomo" in problem:
            no_objectives = 4

        content = open(final_frontier_file).readlines()
        print final_frontier_file
        objectives = []
        for c in content:
            objectives.append(map(float, c.split(',')[-1*(no_objectives):]))
            assert(len(objectives[-1]) == no_objectives), "Something is wrong"

        final_cp_frontier_file = "./FinalFrontier/" + problem + "_" + algorithm + "_" + str(population) + "_" + str(repeat) + ".csv"
        import csv

        with open(final_cp_frontier_file, "wb") as f:
            writer = csv.writer(f)
            writer.writerows(objectives)
        # import pdb
        # pdb.set_trace()