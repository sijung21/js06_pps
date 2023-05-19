
from pickle import TRUE
import sys
import os
import time
import vlc

import cv2
import numpy as np
import pandas as pd
from multiprocessing import Process, Queue
import multiprocessing as mp

from PyQt5.QtGui import QPixmap, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QLabel
from PyQt5.QtCore import QPoint, Qt, pyqtSlot, QTimer
from PyQt5 import uic

from video_thread_mp import CurveThread
import video_thread_mp
import save_db
import save_path_info
from js06_settings import JS06_Setting_Widget
from visibility_widget import Vis_Chart
import js06_log

class JS06MainWindow(QWidget):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "ui/js06_1920_new_new.ui")
        uic.loadUi(ui_path, self)
        # flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint if TRUE else Qt.FramelessWindowHint)
        # # flags = Qt.WindowFlags(Qt.FramelessWindowHint)
        # self.setWindowFlags(flags)
        # self.setAttribute(Qt.WA_NoSystemBackground, True)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        self.rtsp_path = save_path_info.get_data_path("SETTING", "camera_ip")        

        # 실시간 카메라 영상을 출력할 QFrame을 선언
        self.video_frame = QFrame()        
        # layout 위젯에 QFrame 위젯을 탑재
        self.verticallayout.addWidget(self.video_frame)
        
        # self.timer = QTimer()
        # self.timer.start(1000)
        # self.timer.timeout.connect(self.timeout_run)    
  
        # 카메라 IP 주소, 계정, 비밀번호를 rtsp 문법 구조에 맞게 선언
        # VIDEO_SRC3 = f"rtsp://admin:sijung5520@{self.rtsp_path}/profile5/media.smp"
        self.rtsp_path = "121.149.204.221" 
        VIDEO_SRC3 = f"rtsp://admin:sijung5520@{self.rtsp_path}/profile2/media.smp"
        CAM_NAME = "PNM_9030RV"
        # 송수신 시작 함수
        self.onCameraChange(VIDEO_SRC3, CAM_NAME, "Video")
        
    @pyqtSlot(str)        
    def onCameraChange(self, url, camera_name, src_type):
        """Connect the IP camera and run the video thread."""
        
        # 실시간 카메라 영상 출력 부분        
        # Vlc 옵션 설정
        args = [
            "--aspect-ratio",
            "11:3"
            "--rtsp-frame-buffer-size",
            "1500000"
        ]

        self.instance = vlc.Instance(args)
        self.instance.log_unset()
        self.media_player = self.instance.media_player_new()
        
        # 실행 OS가 윈도우일 경우 설정
        if sys.platform == 'win32':
            self.media_player.set_hwnd(self.video_frame.winId())
            
        # 전송방식이 rtsp일 경우
        if url[:4] == "rtsp":
            # vlc instance에 url 입력
            self.media_player.set_media(self.instance.media_new(url))
            self.media_player.video_set_aspect_ratio("3:2")
            # vlc 시작
            self.media_player.play()
        else:
            pass
    def timeout_run(self):
        """Print the current time."""
        current_time = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(time.time()))
        self.test_label = QLabel('Label111111', self)
        self.real_time_label.setText(current_time)
        # self.real_time_label.raise_()
        
    def keyPressEvent(self, e):
        """Override function QMainwindow KeyPressEvent that works when key is pressed"""
        if e.key() == Qt.Key_Escape:
            sys.exit()
            
        if e.key() == Qt.Key_F:
            self.widget_toggle_flag()
    def widget_toggle_flag(self):
        """ JS06 메인 화면 풀 스크린 토글 기능 함수"""
        if self.windowState() & Qt.WindowFullScreen:
            self.showNormal()
        else:
            self.showFullScreen()
        
if __name__ == '__main__':        
    
    # JS06 메인 윈도우 실행
    app = QApplication(sys.argv)
    ui = JS06MainWindow()
    ui.show()
    sys.exit(app.exec_())