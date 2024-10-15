#!/usr/bin/env python3

import board
import adafruit_ltr390
import time
from datetime import datetime

i2c= board.I2C()
ltr390= adafruit_ltr390.LTR390(i2c)
data_file= "/tmp/ltr390.txt"

with open(data_file, "a") as file:
    file.write("# LTR390UV data.\n" \
               "# Started monitoring at {}\n" \
               "# Per line, the data items are:\n" \
               "# * timestamp\n" \
               "# * the currently measured ambient light level\n" \
               "# * the calculated LUX value\n" \
               "# * the calculated UV value\n" \
               "# * the calculated UV index value, based upon the rated sensitivity of 1 UVI per 2300 counts " \
                    "at 18X gain factor and 20-bit resolution\n".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
while True:

    timestamp= datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    sensor_reading= "{},{},{},{},{}\n".format(timestamp,ltr390.light,ltr390.lux,ltr390.uvs,ltr390.uvi)

    with open(data_file, "a") as file:
        file.write(sensor_reading)

    time.sleep(5)
