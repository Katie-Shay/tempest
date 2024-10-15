import pandas as pd
from datetime import datetime, timedelta

data = pd.read_csv('/tmp/pms5003.txt', comment="#", sep=",", header=None,
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
    return data.mean()

def get_24_hour_avgs():
    data=get_data_subset(24,"hours")
    return data.mean()

def get_annual_avgs():
    data=get_data_subset(52,"weeks")
    return data.mean()

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

def main():

    print("Air Quality Index (PM2.5): {}".format(calculate_pm25_aqi()))
    print("Air Quality Index (PM10): {}".format(calculate_pm10_aqi()))

    data= get_24_hour_avgs()
    print("24hr avg PM1: {}".format(data['pm1']))
    print("24hr avg PM2.5: {}".format(data['pm25']))
    print("24hr avg PM10: {}".format(data['pm10']))
    print("24hr avg PM1_atmo: {}".format(data['pm1_atmo']))
    print("24hr avg PM25_atmo: {}".format(data['pm25_atmo']))
    print("24hr avg PM10_atmo: {}".format(data['pm10_atmo']))
    print("24hr avg PM03: {}".format(data['part03']))
    print("24hr avg PM05: {}".format(data['part05']))
    print("24hr avg PM1: {}".format(data['part1']))
    print("24hr avg PM2.5: {}".format(data['part25']))
    print("24hr avg PM5: {}".format(data['part5']))
    print("24hr avg PM10: {}".format(data['part10']))

main()
