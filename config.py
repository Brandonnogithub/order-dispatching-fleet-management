data_path="data/process/order_201611.csv"

n_drivers=[35449, 35284, 37460, 39509, 40453, 38122, 35976, 37131, 36799, 38947, 40996, 40995, 38651, 37496, 38364, 38388, 40101, 41894, 42807, 40282, 38500, 39279, 38785, 40885, 42889, 43257, 41317, 40096, 40771, 40297]    # driver number of each day

# time step
order_delay=1

N_GIRD_X = 15
N_GRID_Y = 17

# the real number of drivers in one day
driver_bias = 0.3 * 0.1

# move 3 in each time step
speed_car = 3

# whether predict future situation when doing fleet management
pred_future = False

# whether do fleet management
do_fleet = True

# random seed
random_state = 20191230

# ratio of unman cars
ratio_unman = 1

# for debug
count = 0