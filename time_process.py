import pickle
import numpy as np

dict = pickle.load(open('time.p'))
problems = sorted(dict.keys())
print  ', '.join(['Problem', 'MOEAD', 'NSGAII', 'SPEA2'])
for problem in problems:
    print problem,
    algorithms = sorted(dict[problem].keys())
    # print algorithms
    # print algorithms
    for algorithm in algorithms:
        print round(np.mean(dict[problem][algorithm]), 3),
    print