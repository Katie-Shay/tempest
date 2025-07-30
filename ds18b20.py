#!/usr/bin/env python3
from w1thermsensor import W1ThermSensor, Sensor, Unit
from datetime import datetime
import time
from prometheus_client import Gauge, CollectorRegistry, push_to_gateway

# Prometheus
push_gateway_url= "localhost:9091"
job_name= "DS18B20"
instance_name= "Tempest"
registry= CollectorRegistry()
pgw_ds18b20= Gauge('DS18B20', 'Data reported by DS18B20', ['label_name'], registry=registry)

# Data Log File
data_file= "/home/cass/tempest/data/ds18b20.txt"
with open(data_file, "a") as file:
    file.write("# DS18B20 data.\n" \
               "# Started monitoring at {}\n" \
               "# Per line, the data items are:\n" \
               "# * Timestamp\n" \
               "# * sensor id\n" \
               "# * Temperature in Celsius\n" \
               "# * Temperature in Fahrenheit\n" \
               "# * Temperature in Kelvin\n".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))


while True:

    for sensor in W1ThermSensor.get_available_sensors([Sensor.DS18B20]):

        timestamp= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        temperature_all_units= sensor.get_temperatures([Unit.DEGREES_C,
                                                        Unit.DEGREES_F,
                                                        Unit.KELVIN])

        sensor_reading= "{},{},{},{},{}\n".format(timestamp,sensor.id,temperature_all_units[0],temperature_all_units[1],temperature_all_units[2])

        with open(data_file,"a") as file:
            file.write(sensor_reading)

        pgw_ds18b20.labels("{} Temp in Celsius".format(sensor.id)).set(temperature_all_units[0])
        pgw_ds18b20.labels("{} Temp in Fahrenheit".format(sensor.id)).set(temperature_all_units[1])
        pgw_ds18b20.labels("{} Temp in Kelvin".format(sensor.id)).set(temperature_all_units[2])

        push_to_gateway(push_gateway_url, job=job_name, registry=registry, grouping_key={'instance': instance_name})

    time.sleep(5)
