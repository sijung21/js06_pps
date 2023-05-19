
#!/usr/bin/env python3
import os
from tkinter import image_names
import pandas as pd
import numpy as np

import cv2
from multiprocessing import Process, Queue
import multiprocessing as mp
import datetime
import time

from PyQt5 import QtWidgets, QtGui, QtCore

import target_info
import save_path_info
import js06_log

def producer(q):
    proc = mp.current_process()
    
    rtsp_path = save_path_info.get_data_path("SETTING", "camera_ip")
    
    
    while True:
        epoch = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        
        # 5초에 한번
        # if int(epoch[-2:]) % 10 == 00:
        
        # 1분에 한번
        if epoch[-2:] == "00":
            print(epoch)
            try:
                target_name, left_range, right_range, distance = target_info.get_target("PNM_9030V")
                
                if len(left_range) < 4:
                    q.put("0")
                    time.sleep(5)
                    continue
                else:                    
                    pass
                
                cap = cv2.VideoCapture(f"rtsp://admin:sijung5520@{rtsp_path}/profile2/media.smp")
                # cap = cv2.VideoCapture(f"rtsp://admin:sijung5520@192.168.100.132/profile2/media.smp")
                ret, cv_img = cap.read()
                
                if ret:
                    visibility = target_info.minprint(epoch[:-2], left_range, right_range, distance, cv_img)
                    
                    img_path = save_path_info.get_data_path('Path', 'image_path')
                    
                    try:
                        os.makedirs(img_path)
                    except Exception as e:
                        pass
                    
                    cv2.imwrite(f'{img_path}/{epoch[:-2]}.jpg', cv_img)
                    
                    cap.release()
                    
                    
                    q.put(visibility)
                    # time.sleep(10)
            except Exception as e:
                print(e)
                cap.release()
                cap = cv2.VideoCapture(f"rtsp://admin:sijung5520@{rtsp_path}/profile2/media.smp")                
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


        
