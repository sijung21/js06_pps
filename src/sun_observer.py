import ephem
from datetime import datetime
import pytz
import time



def sun_observer(now_time):
    
    
    latitude = '37.5665'  # 서울의 위도
    longitude = '126.9780'  # 서울의 경도
    
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
    seoul_timezone = pytz.timezone('Asia/Seoul')
    
    sunrise_time = sunrise.replace(tzinfo=pytz.utc).astimezone(seoul_timezone).time()
    sunset_time = sunset.replace(tzinfo=pytz.utc).astimezone(seoul_timezone).time()
    
    now = datetime.fromtimestamp(now_time).time()
    
    if sunrise_time <= now <= sunset_time:
        # print("daytime")
        return "daytime"
    else:
        return "nighttime"
        # print("nighttime")

    
    
    
    
    
    
    
    
    