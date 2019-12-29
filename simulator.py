import config
import numpy as np
import random
from random import sample
from utils import load_csv, random_tuple, map_str2int, hamming_dis


class Grid():
    '''
    class of one grid
    '''
    def __init__(self, x, y, n):
        self.x = x  # pos x
        self.y = y  # pos y
        self.n = n  # car number

        self.coming_list = []   # the list cotains the coming cars of each feature time steps
        self.orders = []        # the orders in this pos
        self.income = 0         # update when order responsed
        self.select = []

    def random_(self):
        temp = [i for i in range(len(self.orders))]
        if self.n >= len(self.orders):
            self.select = temp
        else:
            self.select = sample(temp, n)
            self.select.sort()


class Order():
    '''
    class of one order
    '''
    def __init__(self, t_s, dur, sx, sy, dx, dy, f_p=1):
        self.t_s = t_s  # start time
        self.dur = dur  # duration
        self.sx = sx    # start pos x
        self.sy = sy    # start pos y
        self.dx = dx    # destination pos x
        self.dy = dy    # destination pos y
        self.delay = config.order_delay     # last time of this order
        if f_p == 1:
            self.p = self.price_1()         # price, initil in run method of simulator
        else:
            self.p = 0

    def price_1(self):
        '''
        a: order data
        p = 1.9 * max(0,(d - 2)) + 8  don't cosider time
        '''
        d = hamming_dis(self.sx, self.sy, self.dx, self.dy)
        return 1.9 * max(0, (d-2)) + 8


def random_driver_init(dis, n):
    x, y = len(dis), len(dis[0])
    samples = random_tuple(x, y, n)
    for sample in samples:
        dis[sample[0], sample[1]].n += 1


def average_driver_init(dis, n):
    x, y = len(dis), len(dis[0])
    n_grids = x * y
    base = int(n / n_grids)
    for i in range(x):
        for j in range(y):
            dis[i][j].n += base
    left_d = n - n_grids * base
    random_driver_init(dis, left_d)
    assert np.sum(dis) == n, "Distribution wrong by average!"


def gaussian_driver_init(dis, n):
    pass



class Simulator():
    def __init__(self, data_path=config.data_path, f_price=1):
        # build grids, which contanins the distribution of drivers
        self.grids = [[Grid(i, j, 0) for j in range(config.N_GRID_Y)] for i in range(config.N_GIRD_X)]

        # build time line
        self.t = 0
        self.day = 1

        # laod data
        self.data = list(map(map_str2int, load_csv(data_path)))

        # calculate price and build order
        temp_data = [Order(a[0], a[1], a[2], a[3], a[4], a[5], f_price) for a in self.data]
        self.data = temp_data

        self.total_order = self.data.shape[0]
        self.n_driver_list = config.n_drivers

        # eval metric
        self.income = 0
        self.rep_order = 0  # responsed order
        self.n_wait = 0     # total waiting order
        self.orr

        # others
        self.last_id = 0    # recorder the access index of data, used for get_t_order func
        
        print("Build simulator finished!")


    def get_t_order(self):
        '''
        get all order in time step self.t
        '''
        res = self.data[self.last_id:]
        for i in range(self.last_id, self.total_order):
            if self.data[i].t_s > self.t:
                res = self.data[self.last_id:i]
                self.last_id = i
                break
        return res


    def run(self, policy=None, driver_init=random_driver_init, t_end=None):
        '''
        policy: the mathcing algorithm
        f_price: the function of price
        dirver_init: how the drivers are initialized
        t_end: end time, real end time = t_end - 1
        '''
        self.policy = policy()

        # initial driver distribution
        driver_init(self.grids, self.n_driver_list[self.day-1])

        # start simulator
        while self.t < t_end:
            print("eval time %d" % self.t)
            # get new order
            t_orders = self.get_t_order()
            # dispatch new order
            self.dispatch_order2grid(t_orders)
            # match order with cars
            self.policy.match(self.grids)
            # update stats
            self.update_grid_state()

            # t + 1 and update the order state
            self.update_grid_coming
            self.t += 1

        print("Finish\n")


    def dispatch_order2grid(self, t_orders):
        '''
        dispatch orders to each grid (You can finish this step in preprocess. I do it jsut for simulator the true situation)
        t_orders: list of Order class
        '''
        # cluster
        dispatch_list = [[[] for i in config.N_GRID_Y] for j in config.N_GIRD_X]
        for order in t_orders:
            dispatch_list[order.sx][order.sy].append(order)

        # dispatch
        for i in range(config.N_GIRD_X):
            for j in range(config.N_GRID_Y):
                self.grids[i][j].orders += dispatch_list[i][j]      # some order remians


    def update_grid_coming(self):
        '''
        after t + 1, some car reaches destination. update
        '''
        for i in range(config.N_GIRD_X):
            for j in range(config.N_GRID_Y):
                # car comes
                grid = self.grids[i][j]
                # update dur
                for i in grid.coming_list:
                    i.dur -= 1
                # sort by dur
                grid.coming_list.sort(key=lambda x:x.dur)
                final_order_idx = len(grid.coming_list)
                for k in range(final_order_idx):
                    if grid.coming_list[k].dur != 0:   # not reaches
                        final_order_idx = k
                        break
                # car number update
                grid.n += final_order_idx
                # coming list update
                grid.coming_list = grid.coming_list[final_order_idx:]

                # update waiting order delay
                 


    def update_grid_state(self):
        '''
        after match, car starts
        '''
        for i in range(config.N_GIRD_X):
            for j in range(config.N_GRID_Y):
                # car leaves
                grid = self.grids[i][j]
                grid.n -= len(grid.select)
                grid.select.reverse()
                for i in grid.select:   # order number
                    # update income
                    grid.income += grid.orders[i].p
                    # add to destination grid coming list
                    self.grids[grid.orders[i].dx][grid.orders[i].dy].coming_list.append(grid.orders[i])
                    # remove from old
                    del grid.orders[i]
                grid.select = []


    def eval(self):
        '''
        eval ADI and ORR
        '''
        # ADI
        for i in range(config.N_GIRD_X):
            for j in range(config.N_GRID_Y):
                self.income += self.grids[i][j].income

        # ORR
        for i in range(self.total_order):
            if self.data[i].t_s >= self.t:
                self.n_wait = i
                break
            if self.data[i].delay >= 0:
                self.rep_order += 1
        self.orr = self.rep_order / self.n_wait

        print("ADI is %d" % self.income)
        print("ORR is %.4f" % self.orr)