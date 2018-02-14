#!/usr/bin/python3
from multiprocessing import Pool
import time

from pi_monte_carlo import NB_TRIALS, estimated_pi, monte_carlo_trials

# Number of cores to use
NB_CORES = 8


def calculate_pi_pool(nb_processes, nb_trials):
    """Calculate an estimate of pi using Monte Carlo method.

    Will perform `nb_trials` trials distibuted on `nb_cores` processes.
    For best result, the number of spawned processes should match the number
    of available CPU / cores of the machine performing the operation.

    Arguments:
        nb_processes (int): The number of processes to spawn
        nb_trials (int): The number of trials for Monte Carlo estimate

    Returns:
        (float): A pi estimate
    """
    res = []
    # Launch a pool of `nb_processes` processes
    # This simple approach does not allow to manipulate process individually
    with Pool(nb_processes) as p:
        res = p.map(monte_carlo_trials,
                    [round(nb_trials / nb_processes)] * nb_processes)

    return estimated_pi(sum(res), nb_trials)


if __name__ == '__main__':
    nb_cores = 8
    start = time.time()
    estimate = calculate_pi_pool(NB_CORES, NB_TRIALS)
    print("Result: {} in {} s".format(estimate, time.time() - start))
