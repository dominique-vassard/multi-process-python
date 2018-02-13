#!/usr/bin/python3
import time

from pi_monte_carlo import NB_TRIALS, estimated_pi, monte_carlo_trials


if __name__ == '__main__':
    start = time.time()
    res = estimated_pi(monte_carlo_trials(NB_TRIALS), NB_TRIALS)
    print("Result: {} in {} s".format(res, time.time() - start))
