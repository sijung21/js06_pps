import os
import logging
import save_path_info

# 로그 생성
logger = logging.getLogger(__name__)

# 로그의 출력 기준 설정
logger.setLevel(logging.DEBUG)

# log 출력 형식
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# log 출력
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


log_path_text = save_path_info.get_data_path('log_path')

try:
    log_save_path = os.path.join(log_path_text)
    os.makedirs(log_save_path)
except Exception as e:
    pass



# log를 파일에 출력
file_handler = logging.FileHandler('my.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

for i in range(10):
	logger.info(f'{i}번째 방문입니다.')
    
logger.info(f'hahahahahahaha')