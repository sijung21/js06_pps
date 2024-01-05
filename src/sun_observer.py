import ephem
from datetime import datetime
import pytz
import time

import save_path_info


def sun_observer(now_time):
    
    
    
    latitude = save_path_info.get_data_path('SETTING', 'latitude')  # 서울의 위도
    longitude = save_path_info.get_data_path('SETTING', 'longitude')  # 서울의 경도
    
    # Observer 객체 생성
    observer = ephem.Observer()
    observer.lat = latitude
    observer.lon = longitude
    
    
    # 일출과 일몰 시간 계산
    sun = ephem.Sun()
    sun.compute(observer)
    sunrise = observer.next_rising(sun).datetime()
    sunset = observer.next_setting(sun).datetime()
    
    # 서울 타임존 설정
    time_zone = save_path_info.get_data_path('SETTING', 'timezone')
    seoul_timezone = pytz.timezone(f'{time_zone}')
    
    sunrise_time = sunrise.replace(tzinfo=pytz.utc).astimezone(seoul_timezone).time()
    sunset_time = sunset.replace(tzinfo=pytz.utc).astimezone(seoul_timezone).time()
    
    now = datetime.fromtimestamp(now_time).time()
    
    if sunrise_time <= now <= sunset_time:
        # print("daytime")
        return "daytime"
    else:
        return "nighttime"
        # print("nighttime")

    
    
    
    
    
    
    
    
    