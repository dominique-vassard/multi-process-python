#!/usr/bin/python3
from multiprocessing import Process, Value, Lock, cpu_count
import time
import random

from pi_monte_carlo import NB_TRIALS, estimated_pi

# Number of cores to use
NB_CORES = cpu_count()


class Worker(Process):
    _nb_trials = 0
    _lock = None
    _nb_ok = None

    def __init__(self, nb_trials, nb_ok, lock):
        self._nb_trials = nb_trials
        self._lock = lock
        self._nb_ok = nb_ok
        super(Worker, self).__init__()

    def run(self):
        """Peform `nb_trials` monte carlo estimate.
        And then put results in nb_ok

        When subclassing Process, when it is started, method `run` will
        automatically called.

        There is two steps here:
          - First, perform the trials
          - Then, update shared resource

        Shared resource should be use only when required, because
        locking/writing process is time-consuming.

        Arguments:
            nb_trials (int): The number of monte carlo trials
            nb_ok (Value): Shared resource for the number of valid result
            lock (Lock): The lock to use to access shared resource
        """

        # First perform the trials
        # Do not use shared resource because other processes doesn't need to
        # know about computation step
        nb_in_quarter_results = 0
        for i in range(self._nb_trials):
            x = random.uniform(0, 1)
            y = random.uniform(0, 1)
            if x * x + y * y <= 1.0:
                nb_in_quarter_results += 1

        # Finally update shared resource
        # Do it only once, then processes doesn't struggle with each other to
        # update it
        with self._lock:
            self._nb_ok.value += nb_in_quarter_results


def calculate_pi_processes(nb_processes, nb_trials):
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
    # Launch a determined number (nb_processes) processes
    # This approach allow to manipulate process individually
    # However, results has to be managed by processes themselves
    #
    #  In order to globally manage result
    #  There's a necessity to use some shared resource
    #  And because of its shared behaviour, Locks must be used in order to
    #  avoid concurrrency problems (If multiple processes trying to write in
    #  the variable at the same time, only data from one will be saved!)
    #
    #  WARNING: Lock / Write / Unlock process is time-consuming.
    #  This should be used only when required.
    lock = Lock()
    res = Value('i', 0)
    processes = []
    for i in range(nb_processes):
        p = Worker(round(nb_trials / nb_processes), res, lock)
        processes.append(p)

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    return estimated_pi(res.value, nb_trials)


if __name__ == '__main__':
    nb_cores = 8
    start = time.time()
    estimate = calculate_pi_processes(NB_CORES, NB_TRIALS)
    print("Result: {} in {} s".format(estimate, time.time() - start))
