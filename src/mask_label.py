
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
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QLabel, QGraphicsOpacityEffect
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
                               "ui/mask_test.ui")
        uic.loadUi(ui_path, self)
        self.on_top = True
        
        flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint if self.on_top else Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 실제 지금 PC 시간을 출력
        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout_run) 
            
    def timeout_run(self):
        """Print the current time."""
        current_time = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(time.time()))
        self.real_time_label.setText(current_time)
        
        
if __name__ == '__main__':        
    
    # JS06 메인 윈도우 실행
    app = QApplication(sys.argv)
    ui = JS06MainWindow()
    ui.show()
    sys.exit(app.exec_())