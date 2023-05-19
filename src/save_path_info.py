import os
import pandas as pd
from PyQt5.QtCore import QSettings


# config.ini 파일의 설정값들을 읽어들어 settings에 저장
settings = QSettings('config.ini', QSettings.IniFormat)
    
# logger = js06_log.CreateLogger(__name__)

# def init_data_path():
    
#     try:
#         os.makedirs(f"{save_path}")
#         print("Initialization path settings")
#     except Exception as e:
#         pass
    
#     data_path = [('D:/data', 'D:/images', 'D:/log', '192.168.100.132')]
    
#     cols = ['data_path', 'image_path', 'log_path', 'camera_ip_path']
#     path_info_df = pd.DataFrame(data_path, columns=cols)
    
#     path_info_df.to_csv(file_path, mode="w", index=True)
    
#     # logger.info("Initialization path settings")

def get_data_path(group, key):
    
    get_text = settings.value(f"{group}/{key}")
    return str(get_text)


def set_data_path(group, key, new_value):    
    
    
    settings.setValue(f"{group}/{key}", new_value)
    # path_df = pd.read_csv(file_path)
    
    # old_folder_path = path_df.loc[0, path_name]
    # path_df = path_df.replace({path_name: old_folder_path}, {path_name: new_folder_path})
    
    # path_df.to_csv(file_path, mode="w", index=False)
    
    
        
    
    
    
    
    
    