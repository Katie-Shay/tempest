#!/usr/bin/env python3

from w1thermsensor import W1ThermSensor, Sensor, Unit
from datetime import datetime
import time

data_file= "/tmp/ds18b20.txt"

with open(data_file, "a") as file:
    file.write("# DS18B20 data.\n" \
               "# Started monitoring at {}\n" \
               "# Per line, the data items are:\n" \
               "# * timestamp\n" \
               "# * sensor id\n" \
               "# * temperature in Celsius\n" \
               "# * temperature in Fahrenheit\n" \
               "# * temperature in Kelvin\n".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))


while True:

    for sensor in W1ThermSensor.get_available_sensors([Sensor.DS18B20]):

        timestamp= datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        temperature_all_units= sensor.get_temperatures([Unit.DEGREES_C,
                                                        Unit.DEGREES_F,
                                                        Unit.KELVIN])

        sensor_reading= "{},{},{},{},{}\n".format(timestamp,sensor.id,temperature_all_units[0],temperature_all_units[1],temperature_all_units[2])

        with open(data_file,"a") as file:
            file.write(sensor_reading)

    time.sleep(5)
