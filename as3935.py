import time
from datetime import datetime
import board
import biffobear_as3935

interrupt_pin = board.D7
i2c = board.I2C()
sensor = biffobear_as3935.AS3935_I2C(i2c, interrupt_pin=interrupt_pin)
data_file= "/home/cass/tempest/data/as3935.txt"

with open(data_file, "a") as file:
    file.write("# AS3935 data\n" \
               "# Started monitoring at {}\n" \
               "# Per line, the data items are:\n" \
               "# * Timestamp\n" \
               "# * Event description\n" \
               "# * Strike energy (if applicable)\n" \
               "# * Distance to storm front in km (if applicable)\n".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

sensor.indoor= True

while True:

    timestamp= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sensor_reading=""

    # detect events
    if sensor.interrupt_set:

        # The interrupt_status is cleared after a read, assign it for later access
        event_type = sensor.interrupt_status

        if event_type == sensor.LIGHTNING:
            event= "Lightning"
            sensor_reading= "{},{},{},{}\n".format(timestamp,event,sensor.energy,sensor.distance)

        elif event_type == sensor.DISTURBER:
            event= "Disturber"
            sensor_reading= "{},{}\n".format(timestamp,event)

        with open(data_file,"a") as file:
            file.write(sensor_reading)

    time.sleep(0.5)
