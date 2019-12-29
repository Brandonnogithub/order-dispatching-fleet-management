import config
import numpy as np
import random
from utils import load_csv, random_tuple


def random_driver_init(dis, n):
    shape = dis.shape
    samples = random_tuple(shape[0], shape[1], n)
    for sample in samples:
        dis[sample[0], sample[1]] += 1


def average_driver_init(dis, n):
    shape = dis.shape
    n_grids = shape[0] * shape[1]
    base = int(n / n_grids)
    dis += base
    left_d = n - n_grids * base
    random_driver_init(dis, left_d)
    assert np.sum(dis) == n, "Distribution wrong by average!"


def gaussian_driver_init(dis, n):
    shape = dis.shape
    pass


class Simulator():
    def __init__(self, data_path=config.data_path):
        # build grids, which contanins the distribution of drivers
        self.grids = np.zeros([config.N_GIRD_X, config.N_GRID_Y])

        # build time line
        self.t = 0
        self.day = 1

        # laod data
        self.data = load_csv(data_path)
        self.n_driver_list = config.n_drivers
        
        print("Build simulator finished!")

    def run(self, policy=None, f_price=None, driver_init=None, t_end=None):
        '''
        policy: the mathcing algorithm
        f_price: the function of price
        dirver_init: how the drivers are initialized
        '''
        driver_init(self.grids, self.n_driver_list[self.day-1])
        for time_step in range(self.t, t_end):

        print("Finish")