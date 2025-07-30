#!/usr/bin/env python
from pms5003 import PMS5003
from datetime import datetime
import time
from prometheus_client import Gauge, CollectorRegistry, push_to_gateway

# Sensor Setup
# Raspberry Pi 4 (Raspberry Pi OS)
# GPIO22 and GPIO27 are enable and reset for Raspberry Pi 4
# use "raspi-config" to enable serial, or add
# "dtoverlay=uart0" to /boot/config.txt
pms5003 = PMS5003(device="/dev/ttyAMA0", baudrate=9600, pin_enable="GPIO22", pin_reset="GPIO27")

# Prometheus
push_gateway_url= "localhost:9091"
job_name= "PMS5003"
instance_name= "Tempest"
registry= CollectorRegistry()
pgw_pms5003= Gauge('PMS5003', 'Data reported by PMS5003', ['label_name'], registry=registry)

# Data Log File
data_file= "/home/cass/tempest/data/pms5003.txt"
with open(data_file, "a") as file:
    file.write("# PMS5003 data\n" \
               "# Started monitoring at {}" \
               "# Per line, the data items are:\n" \
               "# * Timestamp\n" \
               "# * PM 1.0 in μg/m³\n" \
               "# * PM 2.5 in μg/m³\n" \
               "# * PM 10 in μg/m³\n" \
               "# * PM 1.0 in μg/m³ atmospheric environment\n" \
               "# * PM 2.5 in μg/m³ atmospheric environment\n" \
               "# * PM 10 in μg/m³ atmospheric environment\n" \
               "# * number of particles >0.3 μm / 0.1 dm³ of air\n" \
               "# * number of particles >0.5 μm / 0.1 dm³ of air\n" \
               "# * number of particles >1.0 μm / 0.1 dm³ of air\n" \
               "# * number of particles >2.5 μm / 0.1 dm³ of air\n" \
               "# * number of particles >5 μm / 0.1 dm³ of air\n" \
               "# * number of particles >10 μm / 0.1 dm³ of air\n".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))


while True:
    sensor_raw_data = pms5003.read()
    timestamp= datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    pm_ug_per_m3=[]
    pm_per_1l_air=[]

    pm_ug_per_m3.append(sensor_raw_data.pm_ug_per_m3(1.0))
    pm_ug_per_m3.append(sensor_raw_data.pm_ug_per_m3(2.5))
    pm_ug_per_m3.append(sensor_raw_data.pm_ug_per_m3(10))
    pm_ug_per_m3.append(sensor_raw_data.pm_ug_per_m3(1.0, atmospheric_environment= True))
    pm_ug_per_m3.append(sensor_raw_data.pm_ug_per_m3(2.5, atmospheric_environment=True))
    pm_ug_per_m3.append(sensor_raw_data.pm_ug_per_m3(None,atmospheric_environment=True))

    pm_per_1l_air.append(sensor_raw_data.pm_per_1l_air(0.3))
    pm_per_1l_air.append(sensor_raw_data.pm_per_1l_air(0.5))
    pm_per_1l_air.append(sensor_raw_data.pm_per_1l_air(1.0))
    pm_per_1l_air.append(sensor_raw_data.pm_per_1l_air(2.5))
    pm_per_1l_air.append(sensor_raw_data.pm_per_1l_air(5))
    pm_per_1l_air.append(sensor_raw_data.pm_per_1l_air(10))

    sensor_reading= "{},{},{}\n".format(timestamp,
                                        ",".join(str(reading) for reading in pm_ug_per_m3),
                                        ",".join(str(reading) for reading in pm_per_1l_air))

    with open(data_file, "a") as file:
        file.write(sensor_reading)

    pgw_pms5003.labels('PM 1.0 in μg/m³').set(sensor_raw_data.pm_ug_per_m3(1.0))
    pgw_pms5003.labels('PM 2.5 in μg/m³').set(sensor_raw_data.pm_ug_per_m3(2.5))
    pgw_pms5003.labels('PM 10 in μg/m³').set(sensor_raw_data.pm_ug_per_m3(10))
    pgw_pms5003.labels('PM 1.0 in μg/m³ atmospheric environment').set(sensor_raw_data.pm_ug_per_m3(1.0, atmospheric_environment= True))
    pgw_pms5003.labels('PM 2.5 in μg/m³ atmospheric environment').set(sensor_raw_data.pm_ug_per_m3(2.5, atmospheric_environment=True))
    pgw_pms5003.labels('PM 10 in μg/m³ atmospheric environment').set(sensor_raw_data.pm_ug_per_m3(None,atmospheric_environment=True))

    pgw_pms5003.labels('number of particles >0.3 μm / 0.1 dm³ of air').set(sensor_raw_data.pm_per_1l_air(0.3))
    pgw_pms5003.labels('number of particles >0.5 μm / 0.1 dm³ of air').set(sensor_raw_data.pm_per_1l_air(0.5))
    pgw_pms5003.labels('number of particles >1.0 μm / 0.1 dm³ of air').set(sensor_raw_data.pm_per_1l_air(1.0))
    pgw_pms5003.labels('number of particles >2.5 μm / 0.1 dm³ of air').set(sensor_raw_data.pm_per_1l_air(2.5))
    pgw_pms5003.labels('number of particles >5 μm / 0.1 dm³ of air').set(sensor_raw_data.pm_per_1l_air(5))
    pgw_pms5003.labels('number of particles >10 μm / 0.1 dm³ of air').set(sensor_raw_data.pm_per_1l_air(10))

    push_to_gateway(push_gateway_url, job=job_name, registry=registry, grouping_key={'instance': instance_name})

    time.sleep(5)
