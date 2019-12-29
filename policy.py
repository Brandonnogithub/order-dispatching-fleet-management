from abc import ABCMeta, abstractmethod


# DF dispatching and fleet management
class BaseDF():
    def __init__(self):
        pass

    @abstractmethod
    def match(self, grids):
        pass


class RandomDF(BaseDF):
    '''
    each order is randomly selected
    '''
    def __init__(self):
        super().__init__()
        print("Random match!")

    def match(self, grids):
        for i in grids:
            for j in i:
                j.random_()


class GreedyDF(BaseDF):
    def __init__(self):
        super().__init__()
        print("Greedy match!")

    def match(self, grids):
        for i in grids:
            for j in i:
                j.greedy_()