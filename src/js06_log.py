import os
import logging
from datetime import datetime
import save_path_info

def CreateLogger(logger_name):
    
    # 로그 생성
    logger = logging.getLogger(logger_name)

    # 로그의 출력 기준 설정
    logger.setLevel(logging.DEBUG)
    # log 출력 형식
    formatter = logging.Formatter('%(asctime)s - %(name)s :%(lineno)s- %(levelname)s - %(message)s')
    
    log_path_text = save_path_info.get_data_path('Path', 'log_path')

    try:
        log_save_path = os.path.join(log_path_text)
        os.makedirs(log_save_path)
    except Exception as e:
        pass
    
    now = datetime.now()
    date = now.strftime('%Y%m%d')
    log_file_name = f'{date}.log'
    file_path = os.path.join(log_save_path, log_file_name)

    # log를 파일에 출력
    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# def debug_log(msg):
#     logger = CreateLogger("MyLogger")
#     logger.debug(msg)

# def info_log(module_name, msg):
#     logger = CreateLogger(module_name)
#     logger.info(msg)

# def error_log(msg):
#     logger = CreateLogger("MyLogger")
#     logger.error(msg)
    
# if __name__ == '__main__':
    # debug_log()
    # debug_log()



