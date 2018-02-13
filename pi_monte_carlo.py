import random


NB_TRIALS = 10000000


def monte_carlo_trials(nb_trials):
    nb_in_quarter_circle = 0
    for i in range(nb_trials):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        if x * x + y * y <= 1.0:
            nb_in_quarter_circle += 1
    return nb_in_quarter_circle


def estimated_pi(nb_in_quarter_circle, nb_trials):
    return nb_in_quarter_circle * 4 / nb_trials
