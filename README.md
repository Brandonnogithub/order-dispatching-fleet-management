# order-dispatching-fleet-management

This is the final project of my algorithm class.

## GPS

change gcj to wgs84

## Clean Data

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

bias = 0.3, ratio_unman = 1, greedy+fm

| driver ratio  | 0.5    | 0.6    | 0.7    | 0.8    | 0.9    | 1
---:|---:|---:|---:|---:|---:|---:
ADI             | 361.48 | 373.56 | 378.58 | 381.47 | 383.26 | **384.05**
ORR             | 0.9359 | 0.9554 | 0.9633 | 0.9675 | 0.9701 | **0.9712**

some order may evry far. So the reward is large. But greedy will not choose these order.

In greedy there are more idle time for each car So the ADI is lower than random.

## To do

fleet management
