#!/usr/bin/env python3
"""
This code is not include AWS Sensor, only Visibility
"""

import traceback
import binascii
import struct
import time

from influxdb import InfluxDBClient, exceptions
import js06_log

logger = js06_log.CreateLogger(__name__)

def SaveDB(vis_value):
    client = InfluxDBClient('localhost', 8086)
    save_time = time.time_ns()
    print("db 접속")
    try:
        client.switch_database("Sijung")
        print("db switch 접속")
        points = [{"measurement": "JS06",
                "tags": {"name": "Sijung"},
                "fields": {"visbility": float(vis_value)},
                "time": save_time}]
        client.write_points(points=points, protocol="json")
        client.close()
        logger.info('data storage')
    except Exception as e:
        
        print(e)
        print("save error")
        
        logger.error(f'save error')
        logger.error(f'{e}')
        # Save every 1 minute.
        # time.sleep(3)
        pass

    
def main():
    for i in range(10000):
        num = i % 10
        SaveDB(num)

if __name__ == '__main__':
    main()