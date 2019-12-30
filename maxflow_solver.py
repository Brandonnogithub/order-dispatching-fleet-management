import numpy as np
import config
from queue import Queue
from utils import hamming_dis, judge_d


class MaxFlowSolver():
    def __init__(self, n):
        self.n = n
        self.weights = np.zeros([n,n],dtype=np.int)  # n = 15*17
        self.weights_sink = np.zeros(n)
        
        self.residual = np.zeros([n,n])
        self.residual_sink = np.zeros(n)

        self.x = 0
        self.y = 0

        self.sumflow = 0


    def _DFS(self):
        '''
        find augment flow by DFS, it's not a standard maxflow, so here dfs is better
        '''
        for i in range(self.n):
            for j in range(self.n):
                if self.residual[i, j] > 0 and self.residual_sink[j] > 0:
                    self.x = i
                    self.y = j
                    return self.residual[i, j] + self.residual_sink[j]
        return 0  # no


    def find_maxflow(self):
        self.sumflow = 0

        augmentflow = self._DFS()

        while(augmentflow):
            self.weights[self.x, self.y] -= augmentflow
            self.weights_sink[self.y] -= augmentflow
            self.residual[self.x, self.y] += augmentflow
            self.residual_sink[self.y] += augmentflow
            
            self.sumflow += augmentflow
            augmentflow = self.DFS()

        return self.residual

    def set_weight(self, n_car, n_order):
        for i in range(self.n):
            for j in range(self.n):
                if (i == j) or (judge_d(i, j) > config.speed_car):
                    self.weights[i, j] = 0
                else:
                    self.weights[i, j] = n_car[i]
        
        for j in range(self.n):
            self.weights_sink[j] = n_order[j]

        self.residual = np.zeros([self.n,self.n])
        self.residual_sink = np.zeros(self.n)