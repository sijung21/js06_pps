
#!/usr/bin/env python3
import os
from tkinter import image_names
import pandas as pd
import numpy as np

import cv2
from multiprocessing import Process, Queue
import multiprocessing as mp
import ephem
from datetime import datetime
import pytz
import time

from PyQt5 import QtWidgets, QtGui, QtCore

import target_info
import save_path_info
import js06_log
from model_print import Tf_model

def producer(q):
    proc = mp.current_process()
    
    rtsp_path = save_path_info.get_data_path("SETTING", "camera_ip")
    cam_id = save_path_info.get_data_path("SETTING", "camera_id")
    cam_pwd = save_path_info.get_data_path("SETTING", "camera_pw")
    view_profile = save_path_info.get_data_path("SETTING", "save_profile")
    
    tf_model = Tf_model()
    
    latitude = '37.5665'  # 서울의 위도
    longitude = '126.9780'  # 서울의 경도
    
    # Observer 객체 생성
    observer = ephem.Observer()
    observer.lat = latitude
    observer.lon = longitude
    
    
    while True:
        epoch = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        
        # 5초에 한번
        # if int(epoch[-2:]) % 10 == 00:
        
        # 1분에 한번
        if epoch[-2:] == "00":
            print(epoch)
            
            # 일출과 일몰 시간 계산
            sun = ephem.Sun()
            sun.compute(observer)
            sunrise = observer.next_rising(sun).datetime()
            sunset = observer.next_setting(sun).datetime()
            
            try:
                target_name, left_range, right_range, distance = target_info.get_target("PNM_9030V")
                
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
                    print(method)
                    if str(method) == "EXT":
                        visibility = target_info.minprint(epoch[:-2], left_range, right_range, distance, cv_img)
                    
                        
                    elif str(method) == "AI":
                        visibility = tf_model.inference(epoch[:-2], left_range, right_range,
                                                           distance, cv_img)
                        
                    
                    img_path = save_path_info.get_data_path('Path', 'image_save_path')
                    img_path = os.path.join(img_path, epoch[:-6])
                    
                    os.makedirs(img_path, exist_ok=True)
                    
                    cv2.imwrite(f'{img_path}/{epoch[:-2]}.jpg', cv_img)
                    
                    cap.release()
                    
                    
                    q.put(visibility)
                    # time.sleep(10)
            except Exception as e:
                print(e)
                cap.release()
                cap = cv2.VideoCapture(f"rtsp://{cam_id}:{cam_pwd}@{rtsp_path}/{view_profile}/media.smp")                
                continue

class CurveThread(QtCore.QThread):
    update_visibility_signal = QtCore.pyqtSignal(str)

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
                    print("visibility: ", visibility)
                    self.logger.info(f'visibility: {visibility}')
                    self.update_visibility_signal.emit(visibility)
                    
            # shut down capture system

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.quit()
        self.wait()


        
