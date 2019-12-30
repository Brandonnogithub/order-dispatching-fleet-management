import config
import numpy as np
import random
from random import sample
from utils import load_csv, random_tuple, map_str2int, hamming_dis, raiseError

test_n = 0


class Grid():
    '''
    class of one grid
    '''
    def __init__(self, x, y, n):
        self.x = x  # pos x
        self.y = y  # pos y
        self.n = n  # car number
        self.n_unman = n # unman car number
        self.unman_left = 0     # left after selecting

        self.coming_list = []   # the list cotains the coming cars of each feature time steps
        self.orders = []        # the orders in this pos
        self.income = 0         # update when order responsed
        self.select = []

    def random_(self):
        temp = [i for i in range(len(self.orders))]
        if self.n >= len(self.orders):
            self.select = temp
            self.unman_left = min(self.n_unman, self.n - len(self.orders))
        else:
            self.select = sample(temp, self.n)
            self.select.sort()
            self.unman_left = 0
        self.mark_order()

    def greedy_(self, t_now, t_end):
        '''
        choose the min distance order (you can't choose dur because you don't know)
        '''
        if self.n >= len(self.orders):
            self.select = [i for i in range(len(self.orders))]
            self.unman_left = min(self.n_unman, self.n - len(self.orders))
        else:
            # if self.n == 0:
            #     return  # no cars
            self.orders.sort(key=lambda x: x.d)
            self.select = [i for i in range(self.n)]
            # count = 0 # number of selected
            # for i in range(len(self.orders)):
            #     if t_now + self.orders[i].dur < t_end:
            #         self.select.append(i)
            #         count += 1
            #         if count == self.n:
            #             break
            # if count < self.n:
            #     for i in range(len(self.orders)-1, -1, -1):
            #         if i not in self.select:
            #             self.select.append(i)
            #             count += 1
            #             if count == self.n:
            #                 break
            #     self.select.sort()

            self.unman_left = 0
        self.mark_order()

    def mark_order(self):
        # test_n += self.n_unman - self.unman_left
        for i in range(self.n_unman - self.unman_left):
            self.orders[self.select[i]].unman = True



class Order():
    '''
    class of one order
    '''
    def __init__(self, t_s, dur, sx, sy, dx, dy, f_p=1, unman=False):
        self.t_s = t_s  # start time
        self.dur = dur  # duration
        self.sx = sx    # start pos x
        self.sy = sy    # start pos y
        self.dx = dx    # destination pos x
        self.dy = dy    # destination pos y
        self.delay = config.order_delay     # last time of this order
        self.d = hamming_dis(self.sx, self.sy, self.dx, self.dy)
        self.unman = unman
        if f_p == 1:
            self.p = self.price_1()         # price, initil in run method of simulator
        else:
            self.p = 0

    def price_1(self):
        '''
        a: order data
        p = 3.8 * max(0,(d - 1)) + 8  don't cosider time
        '''
        return 3.8 * max(0, (self.d-1)) + 8


def random_driver_init(dis, n, unman=False):
    x, y = len(dis), len(dis[0])
    samples = random_tuple(x, y, n)
    for sample in samples:
        dis[sample[0]][sample[1]].n += 1
        if unman:
            dis[sample[0]][sample[1]].n_unman += 1


def average_driver_init(dis, n, unman=False):
    x, y = len(dis), len(dis[0])
    n_grids = x * y
    base = int(n / n_grids)
    for i in range(x):
        for j in range(y):
            if unman:
                dis[i][j].n_unman += base
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
        self.t_end = 0

        # laod data
        self.data = list(map(map_str2int, load_csv(data_path)))

        # calculate price and build order
        temp_data = [Order(a[0], a[1], a[2], a[3], a[4], a[5], f_price) for a in self.data]
        self.data = temp_data

        self.total_order = len(self.data)
        self.n_driver_list = config.n_drivers
        self.n_drivers = int(self.n_driver_list[self.day-1] * config.driver_bias)
        self.n_unmans = int(self.n_drivers * config.ratio_unman)
        # print(self.n_unmans)

        # eval metric
        self.income = 0
        self.rep_order = 0  # responsed order
        self.n_wait = 0     # total waiting order
        self.orr = 0

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
        self.t_end = t_end

        # initial driver distribution
        driver_init(self.grids, self.n_drivers - self.n_unmans)
        driver_init(self.grids, self.n_unmans, unman=True)

        # start simulator
        while self.t < t_end:
            print("eval time %d" % self.t)
            # get new order
            t_orders = self.get_t_order()
            # dispatch new order
            self.dispatch_order2grid(t_orders)
            # match order with cars
            self.policy.match(self.grids, self.t, t_end)

            # update stats
            self.update_grid_state()

            # t + 1 and update the order state
            self.update_grid_coming()
            self.t += 1
            self.check_unman()

        print("Finish\n")


    def dispatch_order2grid(self, t_orders):
        '''
        dispatch orders to each grid (You can finish this step in preprocess. I do it jsut for simulator the true situation)
        t_orders: list of Order class
        '''
        # cluster
        dispatch_list = [[[] for i in range(config.N_GRID_Y)] for j in range(config.N_GIRD_X)]
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
                for k in grid.coming_list:
                    k.dur -= 1
                # sort by dur
                grid.coming_list.sort(key=lambda x:x.dur)
                final_order_idx = len(grid.coming_list)
                for k in range(final_order_idx):
                    if grid.coming_list[k].dur != 0:   # not reaches
                        final_order_idx = k
                        break
                    elif grid.coming_list[k].unman:
                        grid.n_unman += 1
                # car number update
                grid.n += final_order_idx
                # coming list update
                grid.coming_list = grid.coming_list[final_order_idx:]

                # update waiting order delay
                for k in grid.orders:
                    k.delay -= 1
                for k in range(len(grid.orders)-1, -1, -1):
                    if grid.orders[k].delay < 0:
                        del grid.orders[k]  # order out of time


    def update_grid_state(self):
        '''
        after match, car starts
        '''
        for i in range(config.N_GIRD_X):
            for j in range(config.N_GRID_Y):
                # car leaves
                grid = self.grids[i][j]
                grid.n -= len(grid.select)
                grid.n_unman = grid.unman_left
                grid.unman_left = 0
                # assert grid.n >= 0
                grid.select.reverse()
                for k in grid.select:   # order number
                    # update income
                    t_bias = (self.t + grid.orders[k].dur) - self.t_end
                    if t_bias <= 0:
                        t_bias = 1
                    else:
                        t_bias = (self.t_end - self.t) / grid.orders[k].dur
                    grid.income += grid.orders[k].p * t_bias
                    # add to destination grid coming list
                    self.grids[grid.orders[k].dx][grid.orders[k].dy].coming_list.append(grid.orders[k])
                    # remove from old
                    del grid.orders[k]
                grid.select = []


    def check_unman(self):
        res = 0
        for i in range(config.N_GIRD_X):
            for j in range(config.N_GRID_Y):
                res += self.grids[i][j].n_unman
                for order in self.grids[i][j].coming_list:
                    if order.unman:
                        res += 1
        assert res == self.n_unmans, res


    def eval(self):
        '''
        eval ADI and ORR
        '''
        # ADI
        self.income = 0
        for i in range(config.N_GIRD_X):
            for j in range(config.N_GRID_Y):
                self.income += self.grids[i][j].income

        # ORR
        self.rep_order = 0
        for i in range(self.total_order):
            if self.data[i].t_s >= self.t:
                self.n_wait = i
                break
            if self.data[i].delay >= 0:
                self.rep_order += 1
        self.orr = self.rep_order / self.n_wait

        print("ADI is %d" % self.income)
        print("ORR is %.4f" % self.orr)