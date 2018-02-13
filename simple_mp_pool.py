#!/usr/bin/python3
from multiprocessing import Pool
import time

from pi_monte_carlo import NB_TRIALS, estimated_pi, monte_carlo_trials


if __name__ == '__main__':
    nb_cores = 8
    start = time.time()
    with Pool(nb_cores) as p:
        res = p.map(monte_carlo_trials,
                    [round(NB_TRIALS / nb_cores)] * nb_cores)
        est_pi = estimated_pi(sum(res), NB_TRIALS)
        print("Result: {} in {} s".format(est_pi, time.time() - start))
