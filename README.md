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

## Price

start step : 8

base dis: 2 km

price: 1.9 yuan/km

night: 23:00 - 6:00 +20%
