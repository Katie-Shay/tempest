#!/usr/bin/env python
import pandas as pd, time, itertools
from datetime import datetime, timedelta
from prometheus_client import Gauge, CollectorRegistry, push_to_gateway

# Prometheus
push_gateway_url= "localhost:9091"
job_name= "AQI"
instance_name= "Tempest"
registry= CollectorRegistry()
pgw_aqi= Gauge('AQI', 'Based on data reported by AS3935', ['label_name'], registry=registry)

# Data Log File
data_file= "/home/cass/tempest/data/air_quality.txt"
with open(data_file, "a") as file:
    file.write("# Air Quality data.\n" \
               "# Started monitoring at {}\n" \
               "# Per line, the data items are:\n" \
               "# * Timestamp\n" \
               "# * PM2.5 air quality index (data window 24hrs)\n" \
               "# * PM10 air quality index (data window 24hrs)\n" \
               "# * 1hr avg PM 1.0 in μg/m³\n" \
               "# * 1hr avg PM 2.5 in μg/m³\n" \
               "# * 1hr avg PM 10 in μg/m³\n" \
               "# * 1hr avg PM 1.0 in μg/m³ atmospheric environment\n" \
               "# * 1hr avg PM 2.5 in μg/m³ atmospheric environment\n" \
               "# * 1hr avg PM 10 in μg/m³ atmospheric environment\n" \
               "# * 1hr avg number of particles >0.3 μm / 0.1 dm³ of air\n" \
               "# * 1hr avg number of particles >0.5 μm / 0.1 dm³ of air\n" \
               "# * 1hr avg number of particles >1.0 μm / 0.1 dm³ of air\n" \
               "# * 1hr avg number of particles >2.5 μm / 0.1 dm³ of air\n" \
               "# * 1hr avg number of particles >5 μm / 0.1 dm³ of air\n" \
               "# * 1hr avg number of particles >10 μm / 0.1 dm³ of air\n" \
               "# * 8hr avg PM 1.0 in μg/m³\n" \
               "# * 8hr avg PM 2.5 in μg/m³\n" \
               "# * 8hr avg PM 10 in μg/m³\n" \
               "# * 8hr avg PM 1.0 in μg/m³ atmospheric environment\n" \
               "# * 8hr avg PM 2.5 in μg/m³ atmospheric environment\n" \
               "# * 8hr avg PM 10 in μg/m³ atmospheric environment\n" \
               "# * 8hr avg number of particles >0.3 μm / 0.1 dm³ of air\n" \
               "# * 8hr avg number of particles >0.5 μm / 0.1 dm³ of air\n" \
               "# * 8hr avg number of particles >1.0 μm / 0.1 dm³ of air\n" \
               "# * 8hr avg number of particles >2.5 μm / 0.1 dm³ of air\n" \
               "# * 8hr avg number of particles >5 μm / 0.1 dm³ of air\n" \
               "# * 8hr avg number of particles >10 μm / 0.1 dm³ of air\n" \
               "# * 24hr PM 1.0 in μg/m³\n" \
               "# * 24hr PM 2.5 in μg/m³\n" \
               "# * 24hr PM 10 in μg/m³\n" \
               "# * 24hr PM 1.0 in μg/m³ atmospheric environment\n" \
               "# * 24hr PM 2.5 in μg/m³ atmospheric environment\n" \
               "# * 24hr PM 10 in μg/m³ atmospheric environment\n" \
               "# * 24hr number of particles >0.3 μm / 0.1 dm³ of air\n" \
               "# * 24hr number of particles >0.5 μm / 0.1 dm³ of air\n" \
               "# * 24hr number of particles >1.0 μm / 0.1 dm³ of air\n" \
               "# * 24hr number of particles >2.5 μm / 0.1 dm³ of air\n" \
               "# * 24hr number of particles >5 μm / 0.1 dm³ of air\n" \
               "# * 24hr number of particles >10 μm / 0.1 dm³ of air\n" \
               "# * Annual avg PM 1.0 in μg/m³\n" \
               "# * Annual avg PM 2.5 in μg/m³\n" \
               "# * Annual avg PM 10 in μg/m³\n" \
               "# * Annual avg PM 1.0 in μg/m³ atmospheric environment\n" \
               "# * Annual avg PM 2.5 in μg/m³ atmospheric environment\n" \
               "# * Annual avg PM 10 in μg/m³ atmospheric environment\n" \
               "# * Annual avg number of particles >0.3 μm / 0.1 dm³ of air\n" \
               "# * Annual avg number avg of particles >0.5 μm / 0.1 dm³ of air\n" \
               "# * Annual avg number avg of particles >1.0 μm / 0.1 dm³ of air\n" \
               "# * Annual avg number avg of particles >2.5 μm / 0.1 dm³ of air\n" \
               "# * Annual avg number avg of particles >5 μm / 0.1 dm³ of air\n" \
               "# * Annual avg number avg of particles >10 μm / 0.1 dm³ of air\n".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

data = pd.read_csv('/home/cass/tempest/data/pms5003.txt', comment="#", sep=",", header=None,
                   names=['timestamp',
                          'pm1','pm25','pm10','pm1_atmo','pm25_atmo','pm10_atmo',
                          'part03','part05','part1','part25','part5','part10'])

def calculate_timestamps(interval,unit):
    now= datetime.utcnow()
    hours= days= weeks= 0
    if unit == "hours" or unit == "hour":
        hours = interval
    elif unit == "days" or unit== "day":
        days= interval
    elif unit == "weeks" or unit == "week":
        weeks= interval

    start= (now - timedelta(days=days, hours=hours, weeks=weeks)).strftime("%Y-%m-%d %H:%M:%S")
    end= now.strftime("%Y-%m-%d %H:%M:%S")

    return start, end

def get_data_subset(interval=None, unit=None, timestamp_start=None, timestamp_end=None):
    if interval:
        timestamp_start, timestamp_end= calculate_timestamps(interval,unit)

    return data[data['timestamp'].between(timestamp_start,timestamp_end,)]

def get_1_hour_avgs():
    data=get_data_subset(1,"hours")
    return data.mean(numeric_only=True)

def get_8_hour_avgs():
    data=get_data_subset(8,"hours")
    return data.mean(numeric_only=True)

def get_24_hour_avgs():
    data=get_data_subset(24,"hours")
    return data.mean(numeric_only=True)

def get_annual_avgs():
    data=get_data_subset(52,"weeks")
    return data.mean(numeric_only=True)

def calculate_pm25_aqi():

    concentration= round(get_24_hour_avgs()['pm25'],1)
    if concentration <= 9:
        category= "good"
        aqi_low= 0
        aqi_high= 50
        concentration_low= 0
        concentration_high= 9

    elif concentration <= 35.4:
        category="moderate"
        aqi_low= 51
        aqi_high= 100
        concentration_low= 9.1
        concentration_high= 35.4

    elif concentration <= 55.4:
        category="unhealthy for sensitive groups"
        aqi_low= 101
        aqi_high= 150
        concentration_low= 35.5
        concentration_high= 55.4

    elif concentration <= 125.4:
        category="unhealthy"
        aqi_low= 151
        aqi_high= 200
        concentration_low= 55.5
        concentration_high= 125.4

    elif concentration <= 225.4:
        category="very unhealthy"
        aqi_low= 201
        aqi_high= 300
        concentration_low= 125.5
        concentration_high= 225.4

    elif concentration <=325.4:
        category="hazardous"
        aqi_low= 301
        aqi_high= 500
        concentration_low= 225.5
        concentration_high= 325.4

    elif concentration >=325.5:
        category="hazardous"
        aqi_low= 501
        aqi_high= 999
        concentration_low= 325.5
        concentration_high= 99999.9


    aqi= round((aqi_high - aqi_low)/(concentration_high - concentration_low) * (concentration - concentration_low) + aqi_low,0)

    return category, aqi

def calculate_pm10_aqi():

    concentration= round(get_24_hour_avgs()['pm10'],0)
    if concentration <= 54:
        category= "good"
        aqi_low= 0
        aqi_high= 50
        concentration_low= 0
        concentration_high= 54

    elif concentration <= 154:
        category="moderate"
        aqi_low= 51
        aqi_high= 100
        concentration_low= 55
        concentration_high= 154

    elif concentration <= 254:
        category="unhealthy for sensitive groups"
        aqi_low= 101
        aqi_high= 150
        concentration_low= 155
        concentration_high= 254

    elif concentration <= 354:
        category="unhealthy"
        aqi_low= 151
        aqi_high= 200
        concentration_low= 255
        concentration_high= 354

    elif concentration <= 424:
        category="very unhealthy"
        aqi_low= 201
        aqi_high= 300
        concentration_low= 355
        concentration_high= 424

    elif concentration <=604:
        category="hazardous"
        aqi_low= 301
        aqi_high= 500
        concentration_low= 425
        concentration_high= 604

    elif concentration >=605:
        category="hazardous"
        aqi_low= 501
        aqi_high= 999
        concentration_low= 605
        concentration_high= 99999.9


    aqi= round((aqi_high - aqi_low)/(concentration_high - concentration_low) * (concentration - concentration_low) + aqi_low,0)

    return category, aqi

def format_data(data):

    list= []

    list.append(data['pm1'])
    list.append(data['pm25'])
    list.append(data['pm10'])
    list.append(data['pm1_atmo'])
    list.append(data['pm25_atmo'])
    list.append(data['pm10_atmo'])
    list.append(data['part03'])
    list.append(data['part05'])
    list.append(data['part1'])
    list.append(data['part25'])
    list.append(data['part5'])
    list.append(data['part10'])

    return list

def format_avgs_for_pgw(running_avgs):

    labels=[
               "1hr avg PM 1.0 in μg/m³",
               "1hr avg PM 2.5 in μg/m³",
               "1hr avg PM 10 in μg/m³",
               "1hr avg PM 1.0 in μg/m³ atmospheric environment",
               "1hr avg PM 2.5 in μg/m³ atmospheric environment",
               "1hr avg PM 10 in μg/m³ atmospheric environment",
               "1hr avg number of particles >0.3 μm / 0.1 dm³ of air",
               "1hr avg number of particles >0.5 μm / 0.1 dm³ of air",
               "1hr avg number of particles >1.0 μm / 0.1 dm³ of air",
               "1hr avg number of particles >2.5 μm / 0.1 dm³ of air",
               "1hr avg number of particles >5 μm / 0.1 dm³ of air",
               "1hr avg number of particles >10 μm / 0.1 dm³ of air",
               "8hr avg PM 1.0 in μg/m³",
               "8hr avg PM 2.5 in μg/m³",
               "8hr avg PM 10 in μg/m³",
               "8hr avg PM 1.0 in μg/m³ atmospheric environment",
               "8hr avg PM 2.5 in μg/m³ atmospheric environment",
               "8hr avg PM 10 in μg/m³ atmospheric environment",
               "8hr avg number of particles >0.3 μm / 0.1 dm³ of air",
               "8hr avg number of particles >0.5 μm / 0.1 dm³ of air",
               "8hr avg number of particles >1.0 μm / 0.1 dm³ of air",
               "8hr avg number of particles >2.5 μm / 0.1 dm³ of air",
               "8hr avg number of particles >5 μm / 0.1 dm³ of air",
               "8hr avg number of particles >10 μm / 0.1 dm³ of air",
               "24hr PM 1.0 in μg/m³",
               "24hr PM 2.5 in μg/m³",
               "24hr PM 10 in μg/m³",
               "24hr PM 1.0 in μg/m³ atmospheric environment",
               "24hr PM 2.5 in μg/m³ atmospheric environment",
               "24hr PM 10 in μg/m³ atmospheric environment",
               "24hr number of particles >0.3 μm / 0.1 dm³ of air",
               "24hr number of particles >0.5 μm / 0.1 dm³ of air",
               "24hr number of particles >1.0 μm / 0.1 dm³ of air",
               "24hr number of particles >2.5 μm / 0.1 dm³ of air",
               "24hr number of particles >5 μm / 0.1 dm³ of air",
               "24hr number of particles >10 μm / 0.1 dm³ of air",
               "Annual avg PM 1.0 in μg/m³",
               "Annual avg PM 2.5 in μg/m³",
               "Annual avg PM 10 in μg/m³",
               "Annual avg PM 1.0 in μg/m³ atmospheric environment",
               "Annual avg PM 2.5 in μg/m³ atmospheric environment",
               "Annual avg PM 10 in μg/m³ atmospheric environment",
               "Annual avg number of particles >0.3 μm / 0.1 dm³ of air",
               "Annual avg number avg of particles >0.5 μm / 0.1 dm³ of air",
               "Annual avg number avg of particles >1.0 μm / 0.1 dm³ of air",
               "Annual avg number avg of particles >2.5 μm / 0.1 dm³ of air",
               "Annual avg number avg of particles >5 μm / 0.1 dm³ of air",
               "Annual avg number avg of particles >10 μm / 0.1 dm³ of air"]

    for (label,avg) in zip(labels,running_avgs):
        pgw_aqi.labels(label).set(avg)


def main():

    while True:

        timestamp= datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        pm25_aqi= calculate_pm25_aqi()
        pm10_aqi= calculate_pm10_aqi()
        running_avgs= format_data(get_1_hour_avgs()) + format_data(get_8_hour_avgs()) + format_data(get_24_hour_avgs()) + format_data(get_annual_avgs())
        air_quality_data= "{},{},{},{}\n".format(timestamp,pm25_aqi,pm10_aqi,",".join(str(avg) for avg in running_avgs))

        with open(data_file, "a") as file:
            file.write(air_quality_data)

        pgw_aqi.labels('PM2.5 air quality index numeric (data window 24hrs)').set(pm25_aqi[1])
        pgw_aqi.labels('PM10 air quality index numeric (data window 24hrs)').set(pm10_aqi[1])
        format_avgs_for_pgw(running_avgs)

        push_to_gateway(push_gateway_url, job=job_name, registry=registry, grouping_key={'instance': instance_name})

        time.sleep(1800)

main()
