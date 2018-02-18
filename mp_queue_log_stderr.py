#!/usr/bin/python3
import logging
from multiprocessing import (Process, Queue, Value, Lock, cpu_count,
                             log_to_stderr)
import random
import time

from pi_monte_carlo import NB_TRIALS, estimated_pi

# Number of cores to use
NB_CORES = cpu_count()


class Feeder(Process):
    _queue = None
    _data = None
    _logger = None

    def __init__(self, queue, data, logger):
        self._queue = queue
        self._data = data
        self._logger = logger
        super(Feeder, self).__init__()

    def run(self):
        # Put all data in queue
        self._logger.info("Add data to queue")
        for nb_trials in self._data:
            self._queue.put(nb_trials)

        # Add a specific data to identify end of data
        self._queue.put("STOP")


class Worker(Process):
    _queue = None
    _lock = None
    _nb_ok = None
    _logger = None

    def __init__(self, queue, nb_ok, lock, logger):
        self._queue = queue
        self._lock = lock
        self._nb_ok = nb_ok
        self._logger = logger
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
        while True:
            nb_trials = self._queue.get()
            msg = "{}: Treating {} trials".format(self.pid, nb_trials)
            self._logger.info(msg)
            # If the nd of queue is reached, then :
            #   - Add another "end infirmation" (aka posion pill) information
            #     to queue to propagate the information
            #   - End current loop
            if nb_trials == "STOP":
                self._logger.warning("Exiting and propagate poison pill")
                self._queue.put("STOP")
                break

            for i in range(nb_trials):
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

    # Set logging system
    logger = log_to_stderr()
    logger.setLevel(logging.INFO)

    # Queue will be fed by a process, it can also be fed by procedural code
    # or a function
    #
    # Having it fed by a process expose the fact that queue can be used
    # for IPC (Inter Process Communication)
    to_do = [100, 1000000, 900, 1000, 5000, 5000000, 671250, 500000, 150000,
             750000, 1250000, 500, 671250]
    queue = Queue()
    feeder = Feeder(queue, to_do, logger)
    processes.append(feeder)

    for i in range(nb_processes - 1):
        p = Worker(queue, res, lock, logger)
        processes.append(p)

    for p in processes:
        p.start()

    # Queue is ready!
    queue.close()

    for p in processes:
        p.join()

    return estimated_pi(res.value, nb_trials)


if __name__ == '__main__':
    start = time.time()
    estimate = calculate_pi_processes(NB_CORES, NB_TRIALS)
    print("Result: {} in {} s".format(estimate, time.time() - start))
