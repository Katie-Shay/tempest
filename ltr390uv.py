#!/usr/bin/env python3
import board, adafruit_ltr390, time
from datetime import datetime
from prometheus_client import Gauge, CollectorRegistry, push_to_gateway

# Sensor Setup
i2c= board.I2C()
ltr390= adafruit_ltr390.LTR390(i2c)

# Prometheus
push_gateway_url= "localhost:9091"
job_name= "LTR390UV"
instance_name= "Tempest"
registry= CollectorRegistry()
pgw_ltr390uv= Gauge('LTR390UV', 'Data reported by LTR390UV', ['label_name'], registry=registry)

# Data Log File
data_file= "/home/cass/tempest/data/ltr390.txt"
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

    pgw_ltr390uv.labels('Ambient Light Level').set(ltr390.light)
    pgw_ltr390uv.labels('Calculated LUX value').set(ltr390.lux)
    pgw_ltr390uv.labels('Calculated UV value').set(ltr390.uvs)
    pgw_ltr390uv.labels('Calculated UV index value (based upon the rated sensitivity of 1 UVI per 2300 counts at 18X gain factor and 20-bit resolution)').set(ltr390.uvi)

    push_to_gateway(push_gateway_url, job=job_name, registry=registry, grouping_key={'instance': instance_name})

    time.sleep(5)
