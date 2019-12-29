from simulator import Simulator
from policy import RandomDF


def main():
    # 144 time step for one day
    simulator_ = Simulator()
    simulator_.run(policy=RandomDF, t_end=144)
    simulator_.eval()


if __name__ == "__main__":
    main()