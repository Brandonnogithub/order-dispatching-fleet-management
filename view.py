from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']


def view(x, y1, y2, y3=None, name=None, a=None, b=None, pos="upper right"):

    # plot中参数的含义分别是横轴值，纵轴值，颜色，透明度和标签
    plt.plot(x, y1, 'ro-', color='#4169E1', alpha=0.8, label=name[0])
    plt.plot(x, y2, 'ro-', color='#FF8C00', alpha=0.8, label=name[1])
    if y3 is not None:
        plt.plot(x, y3, 'ro-', color='#00FF00', alpha=0.8, label=name[2])

    # 显示标签，如果不加这句，即使加了label='一些数字'的参数，最终还是不会显示标签
    plt.legend(loc=pos)
    plt.xlabel(a)
    plt.ylabel(b)

    plt.show()
    # plt.savefig('demo.jpg')  # 保存该图片


def main():
    # adi_x = [0.1, 0.3, 0.5, 0.7, 0.9]
    # adi_y_random = [199.99, 306.92, 337.27, 354.23, 366.05]
    # adi_y_greedy = [205.76, 294.85, 326.90, 346.86, 359.26]
    # adi_y_greedy_fm = [268.15, 382.73, 388.18, 391.13, 393.99]
    # view(adi_x, adi_y_random, adi_y_greedy, adi_y_greedy_fm, ["random", "greedy", "greedy+fm"], "bias", "ADI")

    # adi_x = [0.1, 0.3, 0.5, 0.7, 0.9]
    # adi_y_random = [0.4843, 0.7484, 0.8260, 0.8689, 0.8996]
    # adi_y_greedy = [0.6357, 0.8024, 0.8613, 0.8973, 0.9196]
    # adi_y_greedy_fm = [0.7683, 0.9692, 0.9772, 0.9815, 0.9857]
    # view(adi_x, adi_y_random, adi_y_greedy, adi_y_greedy_fm, ["random", "greedy", "greedy+fm"], "bias", "ORR")    

    # adi_x = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    # adi_y_greedy_fm = [361.48, 373.56, 378.58, 381.47, 383.26, 384.05]
    # y_base = [382.73, 382.73, 382.73, 382.73, 382.73, 382.73]
    # view(adi_x, adi_y_greedy_fm, y_base, name=["greedy+fm", "half unman"], a="driver ratio", b="ADI", pos="lower right")

    adi_x = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    adi_y_greedy_fm = [0.9359, 0.9554, 0.9633, 0.9675, 0.9701, 0.9712]
    y_base = [0.9692, 0.9692, 0.9692, 0.9692, 0.9692, 0.9692]
    view(adi_x, adi_y_greedy_fm, y_base, name=["greedy+fm", "half unman"], a="driver ratio", b="ORR", pos="lower right")


if __name__ == "__main__":
    main()