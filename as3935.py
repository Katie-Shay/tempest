#!/usr/bin/env python
from datetime import datetime
import time, board, biffobear_as3935, requests
from prometheus_client import Gauge, CollectorRegistry, push_to_gateway

# Sensor Setup
interrupt_pin = board.D7
i2c = board.I2C()
sensor = biffobear_as3935.AS3935_I2C(i2c, interrupt_pin=interrupt_pin)
sensor.indoor= False

# Promethus
push_gateway_url= "localhost:9091"
job_name= "AS3935"
instance_name= "Tempest"
registry= CollectorRegistry()
pgw_as3935= Gauge('AS3935', 'Data reported by AS3935', ['label_name'], registry=registry)

# Data Log File
data_file= "/home/cass/tempest/data/as3935.txt"
with open(data_file, "a") as file:
    file.write("# AS3935 data\n" \
               "# Started monitoring at {}\n" \
               "# Per line, the data items are:\n" \
               "# * Timestamp\n" \
               "# * Event description\n" \
               "# * Strike energy (if applicable)\n" \
               "# * Distance to storm front in km (if applicable)\n".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

while True:

    timestamp= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sensor_reading=""

    pgw_as3935.labels('Lightning').set(0)
    pgw_as3935.labels('Disturber').set(0)
    pgw_as3935.labels("Strike energy").set(0)
    pgw_as3935.labels("Distance to storm front (km)").set(0)

    # detect events
    if sensor.interrupt_set:

        # The interrupt_status is cleared after a read, assign it for later access
        event_type = sensor.interrupt_status

        if event_type == sensor.LIGHTNING:
            event= "Lightning"
            sensor_reading= "{},{},{},{}\n".format(timestamp,event,sensor.energy,sensor.distance)
            pgw_as3935.labels('Lightning').set(1)
            pgw_as3935.labels("Strike energy").set(sensor.energy)
            pgw_as3935.labels("Distance to Storm front (km)").set(sensor.distance)

        elif event_type == sensor.DISTURBER:
            event= "Disturber"
            sensor_reading= "{},{}\n".format(timestamp,event)
            pgw_as3935.labels('Disturber').set(1)

        with open(data_file,"a") as file:
            file.write(sensor_reading)

        push_to_gateway(push_gateway_url, job=job_name, registry=registry, grouping_key={'instance': instance_name})

    push_to_gateway(push_gateway_url, job=job_name, registry=registry, grouping_key={'instance': instance_name})

    time.sleep(1.5)
