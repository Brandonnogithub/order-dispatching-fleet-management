import numpy as np
import config
from queue import Queue
from utils import hamming_dis, judge_d


class MaxFlowSolver():
    def __init__(self, n):
        self.n = n
        self.weights = np.zeros([n,n],dtype=np.int32)  # n = 15*17
        self.weights_sink = np.zeros(n, dtype=np.int32)
        self.weights_source = np.zeros(n, dtype=np.int32)
        
        self.residual = np.zeros([n,n], dtype=np.int32)
        # self.residual_sink = np.zeros(n, dtype=np.int32)
        # self.residual_source = np.zeros(n, dtype=np.int32)

        self.x = 0
        self.y = 0

        self.sumflow = 0


    def _DFS(self):
        '''
        find augment flow by DFS, it's not a standard maxflow, so here dfs is better
        '''
        for i in range(self.n):
            for j in range(self.n):
                if self.weights_source[i] and self.weights[i, j] > 0 and self.weights_sink[j] > 0:
                    self.x = i
                    self.y = j
                    return min(self.weights_source[i], self.weights[i, j], self.weights_sink[j])
        return 0  # no


    def find_maxflow(self):
        self.sumflow = 0

        augmentflow = self._DFS()

        while(augmentflow):
            self.weights_source[self.x] -= augmentflow
            self.weights[self.x, self.y] -= augmentflow
            self.weights_sink[self.y] -= augmentflow
            self.residual[self.x, self.y] += augmentflow
            # self.residual_sink[self.y] += augmentflow
            # self.residual_source[self.x] += augmentflow
            
            self.sumflow += augmentflow
            augmentflow = self._DFS()

        return self.residual

    def set_weight(self, n_car, n_order):
        for i in range(self.n):
            for j in range(self.n):
                if (i == j) or (judge_d(i, j) > config.speed_car):
                    self.weights[i, j] = 0
                else:
                    self.weights[i, j] = n_car[i]
            self.weights_source[i] = n_car[i]
        
        for j in range(self.n):
            self.weights_sink[j] = n_order[j]

        self.residual = np.zeros([self.n,self.n], dtype=np.int32)
        # self.residual_sink = np.zeros(self.n, dtype=np.int32)
        # self.residual_source = np.zeros(self.n, dtype=np.int32)