import config
import numpy as np
from abc import ABCMeta, abstractmethod
from maxflow_solver import MaxFlowSolver
from simulator import Order
from utils import count2xy


# DF dispatching and fleet management
class BaseDF():
    def __init__(self):
        pass

    @abstractmethod
    def match(self, grids, t_now=None, t_end=None):
        pass


class RandomDF(BaseDF):
    '''
    each order is randomly selected
    '''
    def __init__(self):
        super().__init__()
        print("Random match!")

    def match(self, grids, t_now=None, t_end=None):
        for i in grids:
            for j in i:
                j.random_()


def check_unman(grids, with_left=False):
    res = 0
    for i in range(config.N_GIRD_X):
        for j in range(config.N_GRID_Y):
            if with_left:
                res += grids[i][j].unman_left
            else:
                res += grids[i][j].n_unman
            for order in grids[i][j].coming_list:
                if order.unman:
                    res += 1
            if with_left:
                for k in grids[i][j].select:
                    if grids[i][j].orders[k].unman:
                        res += 1
    assert res == 5317, res



class GreedyDF(BaseDF):
    def __init__(self):
        self.n = config.N_GIRD_X * config.N_GRID_Y
        self.maxflow = MaxFlowSolver(self.n)
        self.do_fleet = config.do_fleet
        print("Greedy match!")

    def match(self, grids, t_now=None, t_end=None):
        # check_unman(grids)
        # config.count = 0
        for i in range(len(grids)):
            for j in range(len(grids[0])):
                grids[i][j].greedy_(t_now, t_end)

        # check_unman(grids, True)
        if self.do_fleet:
            fm = self.fleet_management(grids, future=config.pred_future)
            # print(np.sum(fm))
            # make fake orders
            for i in range(self.n):
                ix, iy = count2xy(i)
                for j in range(self.n):
                    jx, jy = count2xy(j)
                    count = len(grids[ix][iy].orders)
                    for _ in range(fm[i,j]):
                        grids[ix][iy].select.append(count)
                        count += 1
                        grids[ix][iy].orders.append(Order(t_now, 1, ix, iy, jx, jy, f_p=2, unman=True))
                        grids[ix][iy].unman_left -= 1
                        # if grids[ix][iy].unman_left < 0:
                        #     print("wwwwww")
        # check_unman(grids, True)


    def fleet_management(self, grids, future=False):
        n_car = [0 for i in range(self.n)]
        n_order = [0 for i in range(self.n)]
        count = 0
        for i in grids:
            for j in i:
                # order left next t
                n_order[count] += len(j.orders) - len(j.select)  # left order
                if future:
                    for order in j.orders:
                        if order.delay == 0:
                            n_order[count] -= 1     # order disappear next t
                    for k in j.seletc:
                        if j.orders[k].delay == 0:
                            n_order[count] += 1     # redu in select
                    # need add new orders
                # car left next t
                n_car[count] += j.unman_left
                if future:
                    for order in j.coming_list:
                        if order.dur == 1 and order.unman:  # reach in next time step and faker order
                            n_car[count] += 1
                    tem_count = j.n_unman - j.unman_left
                    for k in j.select:
                        if tem_count > 0 and j.orders[k].d <= config.speed_car:   # can not use d
                            # can reach in next t
                            target = j.orders[k].dx * config.N_GRID_Y + j.orders[k].dy
                            n_car[target] += 1
                            tem_count -= 1
                count += 1
        # max flow algorithm
        # print(sum(n_car))
        # print(sum(n_order))
        self.maxflow.set_weight(n_car,n_order)
        fm = self.maxflow.find_maxflow()
        return fm
