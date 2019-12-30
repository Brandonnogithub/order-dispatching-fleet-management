import random
import config
from simulator import Simulator
from policy import RandomDF, GreedyDF
from simulator import gaussian_driver_init


def main():
    random.seed(config.random_state)
    # 144 time step for one day
    simulator_ = Simulator()
    simulator_.run(policy=GreedyDF, t_end=144, driver_init=gaussian_driver_init)
    simulator_.eval()


if __name__ == "__main__":
    main()