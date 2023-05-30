import ephem
from datetime import datetime
import pytz

# 현재 날짜와 시간을 얻기 위해 datetime 모듈 사용
now = datetime.now()

# 서울의 위도와 경도 설정
# latitude = '37.5665'  # 서울의 위도
# longitude = '126.9780'  # 서울의 경도
latitude = '33.321349'  # 서울의 위도
longitude = '126.684723'  # 서울의 경도

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
print(seoul_timezone)
# 서울 시간으로 변환
sunrise_seoul = sunrise.astimezone(seoul_timezone).strftime('%Y-%m-%d %H:%M:%S %Z')
sunset_seoul = sunset.astimezone(seoul_timezone)

# 결과 출력
print("현재 날짜 및 시간:", now)
print("일출 시간 (서울):", sunrise_seoul)
print("일몰 시간 (서울):", sunset_seoul)

print(sunrise.replace(tzinfo=pytz.utc))
print(sunrise.replace(tzinfo=pytz.utc).astimezone(seoul_timezone).strftime('%Y-%m-%d %H:%M:%S'))
print(sunset.replace(tzinfo=pytz.utc).astimezone(seoul_timezone).strftime('%Y-%m-%d %H:%M:%S'))
# print(sunset.replace(tzinfo=pytz.utc).astimezone(seoul_timezone) - now)



# 과거 날짜 생성
past_date = datetime(2023, 1, 1)  # 예시: 2023년 1월 1일

# 현재 날짜와 과거 날짜 간의 차이 계산
diff =  past_date-now

# 결과 출력
print("현재 날짜:", now)
print("과거 날짜:", past_date)
print("날짜 차이:", diff.days, "일")
print(diff)