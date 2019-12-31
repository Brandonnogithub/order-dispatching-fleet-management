# order-dispatching-fleet-management

This is the final project of my algorithm course. In this project we use a min-distance greedy + maxflow-based fleet management algorithm to improve the accumumalted income(**ADI**) and order repronse rate(**ORR**).

## Requirement

* python 3.6
* numpy

## Explain for each file

* **/pic**: the result diagrams
* **/report**: our report
* **config.py**: the config file. you can change settings like dirver number here
* **data_process.py**: autoprocess data for simulation
* **gps_utils.py**: change gcj postion into wgs84 positiion
* **main.py**: the main function is here. You can change policy method in main
* **maxflow_solver.py**: a class to solve maxflow problem. But in the project the maxflow problem is special, I didn't implement this solver in standard way.(Which means you can't use this to solve other problem). Good news is this is much faster.
* **policy.py**: Here includes all policies:random and greedy. You can add new policy success from the base class.
* **simulator.py**: a simulator to simulate the real world
* **utils.py**: some utils function
* **view.py**: visualize the results and save pic to /pic
* **README.md**: which you are looking :)

## Clean Data

Data can be download from [didi](<https://outreach.didichuxing.com/app-vue/dataList>)

You just need to put data in the right position and run

```python
formalize_order_data()
sort_orders()
```

remove wrong time

remove far position

total removed: 131566

remaining orders: 6934371

## Grid

about 2km x 2km for each grid, 15 * 17 grids

range: `[[103.89325, 30.547255], [104.20675, 30.852745]]`

split by degree, x(0.0209), y(0.01797)

## Time

time step is 10 mins(600s), all order which are finished in less 1 time step are setted as 1 time step. (About 230281 orders)

## Order

### price

start step : 8

base dis: 2 km

price: 1.9 yuan/km

night: 23:00 - 6:00 +20%

### delay

each order lasts 1 time step

## Driver Bias

About 4,000 drivers in one day. But they won't be online all day. So we add a bias to driver number.

n_driver = bias * n_driver

unman car = n_driver * ratio_unman(ratio)

## Results

ADI, ratio_unman = 0.5

|   bias    | 0.1    | 0.3    | 0.5    | 0.7    | 0.9
---:|---:|---:|---:|---:|---:
random      | 199.99 | 306.92 | 337.27 | 354.23 | 366.05
greedy      | 205.76 | 294.85 | 326.90 | 346.86 | 359.26
greedy+fm   | **268.15** | **382.73** | **388.18** | **391.13** | **393.99**

ORR, ratio_unman = 0.5

|   bias    | 0.1    | 0.3    | 0.5    | 0.7    | 0.9
---:|---:|---:|---:|---:|---:
random      | 0.4843 | 0.7484 | 0.8260 | 0.8689 | 0.8996
greedy      | 0.6357 | 0.8024 | 0.8613 | 0.8973 | 0.9196
greedy+fm   | **0.7683** | **0.9692** | **0.9772** | **0.9815** | **0.9857**

In greedy there are more idle time for each car So the ADI is lower than random.

bias = 0.3, ratio_unman = 1, greedy+fm

| driver ratio  | 0.1    |0.2    | 0.3    | 0.4    | 0.5    | 0.6    | 0.7    | 0.8    | 0.9    | 1
---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:
ADI             | 103.83 | 192.17 | 269.16 | 328.31 | 361.48 | 373.56 | 378.58 | 381.47 | 383.26 | **384.05**
ORR             | 0.3970 | 0.6205 | 0.7737 | 0.8797 | 0.9359 | 0.9554 | 0.9633 | 0.9675 | 0.9701 | **0.9712**

It show if we replace all cars with unman cars, keeping about **86\%** car numbers can get the same performance.

And even you use only 50\% cars the performance is still good.(Unman is the future!)

## To do

fleet management
