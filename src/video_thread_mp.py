
#!/usr/bin/env python3
import os
from tkinter import image_names
import pandas as pd
import numpy as np
from datetime import datetime
import cv2
from multiprocessing import Process, Queue
import multiprocessing as mp
import time

from PyQt5 import QtWidgets, QtGui, QtCore

import target_info
import save_path_info
import js06_log
from model_print import Tf_model
import sun_observer

def producer(q):
    proc = mp.current_process()
    camera_name = save_path_info.get_data_path("SETTING", "camera_name")
    rtsp_path = save_path_info.get_data_path("SETTING", "camera_ip")
    cam_id = save_path_info.get_data_path("SETTING", "camera_id")
    cam_pwd = save_path_info.get_data_path("SETTING", "camera_pw")
    view_profile = save_path_info.get_data_path("SETTING", "save_profile")
    q_list = []
    tf_model = Tf_model()
    
    while True:
        now_time = time.time()
        epoch = time.strftime("%Y%m%d%H%M%S", time.localtime(now_time))
        
        # 5초에 한번
        # if int(epoch[-2:]) % 10 == 00:
        
        # 1분에 한번
        if epoch[-2:] == "00":
            print(epoch)
            
            try:
                target_name, left_range, right_range, distance = target_info.get_target(f"{camera_name}")
                
                if len(left_range) < 4:
                    q.put("0")
                    time.sleep(5)
                    continue
                else:                    
                    pass
                
                cap = cv2.VideoCapture( f"rtsp://{cam_id}:{cam_pwd}@{rtsp_path}/{view_profile}/media.smp")
                # cap = cv2.VideoCapture(f"rtsp://admin:sijung5520@192.168.100.132/profile2/media.smp")
                ret, cv_img = cap.read()
                
                if ret:
                    
                    method = save_path_info.get_data_path("Method", "method")
                    
                    
                                        
                    if str(method) == "EXT":
                        
                        dn_time = sun_observer.sun_observer(now_time)
                        
                        if dn_time == "daytime":
                            visibility = target_info.minprint(epoch[:-2], left_range, right_range, distance, cv_img)
                        else:
                            visibility = tf_model.inference(epoch[:-2], left_range, right_range,
                                                           distance, cv_img)
                    
                        
                    elif str(method) == "AI":
                        visibility = tf_model.inference(epoch[:-2], left_range, right_range,
                                                           distance, cv_img)
                    
                    visibility = float(visibility)
                    ############################ 이미지 저장 #########################
                    img_path = save_path_info.get_data_path('Path', 'image_save_path')
                    img_path = os.path.join(img_path, epoch[:-6])
                    
                    os.makedirs(img_path, exist_ok=True)
                    
                    cv2.imwrite(f'{img_path}/{epoch[:-2]}.jpg', cv_img)
                    
                    cap.release()
                    ############################ 이미지 저장 #########################
                    
                    
                    ####################### 미세먼지 값, 러닝 에버리지 산출 #####################
                    
                    if visibility > 20:
                        visibility = 20
                    elif visibility < 0.01:
                        visibility = 0.01
                    
                    visibility_float = round(visibility, 3)
                    print("visibility : ", visibility_float)
                    q_list_scale = int(save_path_info.get_data_path("SETTING", "running_average"))
                    
                    if len(q_list) == 0 or q_list_scale != len(q_list):
                        q_list = []
                        for i in range(q_list_scale):
                            q_list.append(visibility_float)
                            
                        # print("q 리스트 길이", len(q_list))
                        # logger.info(f"q list length : {len(q_list)}")
                        ra_visibility = np.mean(q_list)
                    else:
                        # logger.info(f"q list length : {len(q_list)}")
                        q_list.pop(0)
                        q_list.append(visibility_float)
                        ra_visibility = np.mean(q_list)  
                    
                    ra_visibility = round(float(ra_visibility), 3)
                    print("ra_visibility : ", ra_visibility)
                    ext = 3.912 / ra_visibility
                    hd = 89
                    pm_value = round((ext*1000/4/2.5)/(1+5.67*((hd/100)**5.8)),2)
                    
                    print("pm_value : ", pm_value)
                    ####################### 시정 미세먼지 값 산출 #####################
                    
                    
                    # Queue에 ra_visibility, pm_value 넣기(메인 함수에 보내려고)
                    q.put(ra_visibility)                                                    
                    q.put(pm_value)                                                     
                    
                    
                    
                    ########################## 산출한 값을 Data Path에 저장(CSV) #########################
                    days = epoch[:-6]
                    print("days", days)
                    vis_folder_path = os.path.join(save_path_info.get_data_path('Path', 'data_csv_path'))
                    print("vis_folder_path", vis_folder_path)
                    vis_file_path = os.path.join(vis_folder_path,f"{days}.csv")
                    print("vis_file_path", vis_file_path)
                    os.makedirs(vis_folder_path, exist_ok=True)
                    
                    if os.path.isfile(vis_file_path):
                        vis_df = pd.read_csv(vis_file_path)
                    else:
                        cols = ["time",'visibility','pm2.5','ra_visibility']
                        vis_df = pd.DataFrame(columns=cols)
                    
                    
                    dt_epoch = datetime.strptime(epoch[:-2], '%Y%m%d%H%M')
                    print("dt_epoch", dt_epoch)
                    vis_df = vis_df.append({'time': dt_epoch,'visibility': visibility,'pm2.5': pm_value,'ra_visibility': ra_visibility}, ignore_index=True)
                    # vis_df = pd.concat(vis_df, pd.DataFrame({'time': dt_epoch,'visibility': visibility,'pm2.5': pm_value,'ra_visibility': ra_visibility}), ignore_index=True)
                    print(vis_df.head())
                    vis_df.to_csv(vis_file_path,mode="w", index=False)
                    ########################## 산출한 값을 Data Path에 저장(CSV) #########################
                    
                    # time.sleep(10)
            except Exception as e:
                print(e)
                cap.release()
                cap = cv2.VideoCapture(f"rtsp://{cam_id}:{cam_pwd}@{rtsp_path}/{view_profile}/media.smp")                
                continue

class CurveThread(QtCore.QThread):
    update_visibility_signal = QtCore.pyqtSignal(float, float)

    def __init__(self, src: str = "", file_type: str = "None", q: Queue = None):
        super().__init__()
        self._run_flag = False
        self.src = src
        self.file_type = file_type
        self.q = q
        self.logger = js06_log.CreateLogger(__name__)


    def run(self):
        self._run_flag = True
        ## 영상 입력이 카메라일 때
        if self.file_type == "Video":
            print("Start curve thread")
            self.logger.info('Start curve thread')
            while self._run_flag:
                if not self.q.empty():
                    visibility = self.q.get()
                    pm_value = self.q.get()
                    self.logger.info(f'visibility: {visibility}')
                    self.logger.info(f'pm25_value: {pm_value}')
                    self.update_visibility_signal.emit(visibility, pm_value)
                    
            # shut down capture system

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.quit()
        self.wait()


        
