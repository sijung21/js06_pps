
import sys
import os
import time
import vlc
import ctypes

import cv2
import numpy as np
import pandas as pd
from multiprocessing import Process, Queue
import multiprocessing as mp

from PyQt5.QtGui import QPixmap, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QLabel
from PyQt5.QtCore import QPoint, Qt, pyqtSlot, QTimer, QDateTime
from PyQt5 import uic

from video_thread_mp import CurveThread
import video_thread_mp
# import save_db
import save_path_info
from js06_settings import JS06_Setting_Widget
from visibility_widget import Vis_Chart
import js06_log
from cloud_animation import Weather_Icon

class JS06MainWindow(QWidget):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "ui/js06_1920_grid_test.ui")
        uic.loadUi(ui_path, self)
        
        

        self.camera_name = ""
        self.video_thread = None
        self.g_ext = None
        self.pm_25 = None
        self.test_name = None
        self.radio_checked = save_path_info.get_data_path("SETTING", "distance_unit")
        self.running_ave_checked = save_path_info.get_data_path("SETTING", "running_average")
        self.visibility_copy = 0
        # self.running_average = 1
        self.q_list = []
        self.q_list_scale = int(save_path_info.get_data_path("SETTING", "running_average"))
        self.rtsp_path = None
        self.logger = js06_log.CreateLogger(__name__)
        self.vis_list = []
        
        # # JS06의 설정 정보들을 초기화 하거나 이미 있으면 패쓰
        # if os.path.isfile("D:/path_info/path_info.csv"):
        #     pass        
        # else:
        #     save_path_info.init_data_path()
        
        self.rtsp_path = save_path_info.get_data_path("SETTING", "camera_ip")

        # 실시간 카메라 영상을 출력할 QFrame을 선언
        # self.video_frame = QFrame()        
        # layout 위젯에 QFrame 위젯을 탑재
        # self.verticallayout.addWidget(self.video_frame)
        
        cam_id = save_path_info.get_data_path("SETTING", "camera_id")
        cam_pwd = save_path_info.get_data_path("SETTING", "camera_pw")
        view_profile = save_path_info.get_data_path("SETTING", "view_profile")
  
        # 카메라 IP 주소, 계정, 비밀번호를 rtsp 문법 구조에 맞게 선언
        VIDEO_SRC3 = f"rtsp://{cam_id}:{cam_pwd}@{self.rtsp_path}/{view_profile}/media.smp"     
        # VIDEO_SRC3 = f"rtsp://admin:sijung5520@121.149.204.221/profile2/media.smp"
        CAM_NAME = save_path_info.get_data_path("SETTING", "camera_name")
        # 송수신 시작 함수
        self.onCameraChange(VIDEO_SRC3, CAM_NAME, "Video")
        
        self.uri = VIDEO_SRC3
        
        
        # 시정 실시간 출력 차트 클래스 선언
        
        self.chart_view = Vis_Chart()
        self.web_verticalLayout.addWidget(self.chart_view.chart_view)
        
        
        # 소산계수, 시정, 미세먼지 산출하는 쓰레드 선언
        self.video_thread = CurveThread(VIDEO_SRC3, "Video", q)
        # # 쓰레드와 시정, 미세먼지 출력 함수를 Signal 연결
        self.video_thread.update_visibility_signal.connect(self.print_data)
        # # 쓰레드 시작
        self.video_thread.start()

        # 실제 지금 PC 시간을 출력
        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout_run)        
        
        # 설정 버튼 클릭시 설정창 출력
        self.settings_button.clicked.connect(self.setting_btn_click)
        
        # 현재 실행 파일 위치 확인
        self.filepath = os.path.join(os.getcwd())
        
        # 구름 애니메이션
        # self.cloud_icon = Weather_Icon(self)
        # self.cloud_icon.setGeometry(940,650,120,80)
        
        
        
        
    
    @pyqtSlot(str)
    def onCameraChange(self, url, camera_name, src_type):
        """Connect the IP camera and run the video thread."""
        
        # 실시간 카메라 영상 출력 부분        
        # Vlc 옵션 설정
        args = [
            "--rtsp-frame-buffer-size",
            "1500000"
        ]

        self.instance = vlc.Instance()
        # self.instance.log_open()
        # self.instance.log_unset()
        # fopen = ctypes.cdll.msvcrt.fopen
        # fopen.restype = vlc.FILE_ptr
        # fopen.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
        # ctypes에 문자열 인자값들을 넣으려면 모두 byte 형태로 변환해줘야 함
        
        # current_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        # f = fopen(bytes(f'vlc_log_{current_time}.log', encoding='utf-8'), b'w')
        
        # self.instance.log_set_file(f)
        
        
        self.media_player = self.instance.media_player_new()
        
        # 실행 OS가 윈도우일 경우 설정
        if sys.platform == 'win32':
            self.media_player.set_hwnd(self.video_frame.winId())
            
        # 전송방식이 rtsp일 경우
        if url[:4] == "rtsp":
            # vlc instance에 url 입력
            self.media_player.set_media(self.instance.media_new(url))
            set_ratio = save_path_info.get_data_path("SETTING", "video_set_aspect_ratio")
            self.media_player.video_set_aspect_ratio(set_ratio)           
            
            # vlc 시작
            self.media_player.play()
             
        else:
            pass
        self.logger.info("Video playback success")
    
    def get_status(self):
        """vlc 플레이어 상태 확인 플레이어가 중단되어 있으면 다시 재연결해주는 함수"""
        if self.media_player.is_playing() == 0:
            print(f'Player is not playing! in '
                    f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(QDateTime.currentSecsSinceEpoch()))}')
            self.media_player.set_media(self.instance.media_new(self.uri))
            self.media_player.play()
        else:
            pass
        
           
    @pyqtSlot(str)
    def print_data(self, visibility):
        """ 메인 화면에 산출된 소산계수로 시정과 미세먼지를 계산 및 표시하는 함수"""
        
        visibility_float = round(float(visibility), 3)
        
        if visibility == "0":
            self.data_storage(0)
            return
        
        if len(self.q_list) == 0 or self.q_list_scale != len(self.q_list):
            self.q_list = []
            for i in range(self.q_list_scale):
                self.q_list.append(visibility_float)
                
            # print("q 리스트 길이", len(self.q_list))
            self.logger.info(f"q list length : {len(self.q_list)}")
            result_vis = np.mean(self.q_list)
        else:
            self.logger.info(f"q list length : {len(self.q_list)}")
            self.q_list.pop(0)
            self.q_list.append(visibility_float)
            result_vis = np.mean(self.q_list)            
        
        self.visibility_copy = round(float(result_vis), 3)
        
        self.radio_checked = save_path_info.get_data_path("SETTING","distance_unit")
        
        if self.radio_checked == None or self.radio_checked == "Km":
            visibility_text = str(self.visibility_copy) + " km"
        elif self.radio_checked == "Mile":
            visibility_mile = round(self.visibility_copy / 1.609, 1)
            visibility_text = str(visibility_mile) + " mi"
        
        self.c_vis_label.setText(visibility_text)
        ext = 3.912 / self.visibility_copy
        hd = 89
        pm_value = round((ext*1000/4/2.5)/(1+5.67*((hd/100)**5.8)),2)
        
        # Error Note: 미세먼지 단위를 ini 파일에 넣으면 깨짐.
        concentration_text = save_path_info.get_data_path("SETTING","concentration_unit")
        pm_text = str(pm_value) + " ㎍/㎥"
        self.c_pm_label.setText(pm_text)
        # influxdb에 시정 값 저장
        self.data_storage(self.visibility_copy)
        
        # vlc 상태 확인
        self.get_status()
        
        
        
    def data_storage(self, vis_data):
        """Store visibility and fine dust values ​​in the database."""

        # save_db.SaveDB(vis_data)
        print("data storage!")
        self.chart_view.appendData(vis_data)
        

    def timeout_run(self):
        """Print the current time."""
        current_time = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(time.time()))
        self.real_time_label.setText(current_time)
        # self.real_time_label.raise_()
        
    @pyqtSlot()
    def setting_btn_click(self):
        """ 설정 버튼 클릭 이벤트를 했을 때 환경설정(Setting) 창을 띄우는 함수 """
        if self.radio_checked == None:
            dlg = JS06_Setting_Widget("Km")
        else:
            dlg = JS06_Setting_Widget(self.radio_checked)
        dlg.show()
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.deleteLater()
        dlg.exec_()
        
        
        self.radio_checked = dlg.radio_flag
        print(self.radio_checked, "변환 완료")
        self.logger.info(f"{self.radio_checked} Conversion done")
        
        if self.radio_checked == None or self.radio_checked == "Km":
            visibility_text = str(self.visibility_copy) + " km"
        elif self.radio_checked == "Mile":
            visibility_mile = round(self.visibility_copy / 1.609, 1)
            visibility_text = str(visibility_mile) + " mi"
            
        self.c_vis_label.setText(visibility_text)
        
        # self.running_ave_checked = dlg.running_ave_checked
        # print(self.running_ave_checked, "변환 완료")
        # self.logger.info(f"{self.running_ave_checked} Conversion done")
        
        self.q_list_scale = int(save_path_info.get_data_path("SETTING", "running_average"))

    def keyPressEvent(self, e):
        """Override function QMainwindow KeyPressEvent that works when key is pressed"""
        if e.key() == Qt.Key_Escape:
            self.logger.info(f"Click the End Program button")
            sys.exit()
            
        if e.key() == Qt.Key_F:
            self.widget_toggle_flag()
        
    def widget_toggle_flag(self):
        """ JS06 메인 화면 풀 스크린 토글 기능 함수"""
        if self.windowState() & Qt.WindowFullScreen:
            self.showNormal()
            self.logger.info(f"View in normal screen")
        else:
            self.showFullScreen()
            self.logger.info(f"View in full screen")

if __name__ == '__main__':    
    
    # MultiProcess 선언
    # MultiProcess의 프로세스 수 고정
    logger = js06_log.CreateLogger(__name__)
    logger.info(f'Start JS06 Program')
    
    mp.freeze_support()
    q = Queue()
    p = Process(name="producer", target=video_thread_mp.producer, args=(q, ), daemon=True)
    logger.info(f'Start video multiprocess')
    p.start()
    
    
    # JS06 메인 윈도우 실행
    app = QApplication(sys.argv)
    ui = JS06MainWindow()
    ui.show()
    logger.info(f'Open JS06 main winodw ')
    sys.exit(app.exec_())
    
