
import datetime
import sys
import os
import time
import math
from typing_extensions import Self
import vlc
import random

import cv2
import numpy as np
import pandas as pd
from multiprocessing import Process, Queue
import multiprocessing as mp

# print(PyQt5.__version__)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QBrush, QColor, QPen, QImage, QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QVBoxLayout, QWidget, QLabel, QInputDialog, QGraphicsScene, QGraphicsView, QFrame, QTabWidget
from PyQt5.QtCore import QPoint, QRect, Qt, QRectF, QSize, QCoreApplication, pyqtSlot, QTimer, QUrl, QDateTime, pyqtSignal, QThread
from PyQt5 import uic
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem

from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtWebEngineCore
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis


from video_thread_mp import CurveThread
import video_thread_mp
import save_db
import save_path_info
from js06_settings import JS06_Setting_Widget
from grafana_view_widget import GraFanaMainWindow

from influxdb import InfluxDBClient

print(pd.__version__)


class ValueWorker(QThread):
    dataSent = pyqtSignal(float)
    
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.alive = True
        
    def run(self):
        while self.alive:
            # data = 5 * random.random()
            client = InfluxDBClient('localhost', 8086)
            save_time = time.time_ns()
            client.switch_database("Sijung")
            query = 'SELECT "visbility" FROM "JS06" ORDER BY "time" DESC LIMIT 1'
            result = client.query(query)
            visiblity = result.get_points()           
            for item in list(visiblity):
                data = item['visbility']
                print(data)
                
            client.close()
            time.sleep(10)
            self.dataSent.emit(data)
    
    def close(self):
        self.alive = False
        
class Vis_Chart(QWidget):
    
    def __init__(self, parent=None, max_value = 50):
        super().__init__(parent)
        
                # chart object
        # self.chart = QChart()
        # self.font = QFont()
        # self.font.setPixelSize(20)        
        # self.font.setBold(3)
        # self.chart.setTitle("Visibility Graph")
        # self.chart.setTitleFont(self.font)
        # self.chart.setTitleBrush(QBrush(QColor("white")))
        # self.chart.setAnimationOptions(QChart.SeriesAnimations)
        # self.chart.layout().setContentsMargins(0,0,0,0)
        # self.chart.setBackgroundRoundness(0)
        
        # self.series = QLineSeries()
        # self.series.setPointLabelsVisible()
        
        # axisBrush = QBrush(QColor("white"))

        # self.series.setName("Visibility")
        
        # axis_x = QValueAxis()
        # axis_x.setTickCount(7)
        # axis_x.setLabelFormat("%i")
        # axis_x.setTitleText("Time")
        # axis_x.setRange(0,max_value)     
        # axis_x.setLabelsBrush(axisBrush)
        # axis_x.setTitleBrush(axisBrush)     
        # self.chart.addAxis(axis_x, Qt.AlignBottom)        
        
        # axis_y = QValueAxis()
        # axis_y.setTickCount(7)
        # axis_y.setLabelFormat("%i")
        # axis_y.setTitleText("Visibility(km)")
        # axis_y.setRange(0, 20)
        # axis_y.setLabelsBrush(axisBrush)
        # axis_y.setTitleBrush(axisBrush)
        # self.chart.addAxis(axis_y, Qt.AlignLeft) 
        
        # self.series.append(1, 15)
        # self.series.append(10, 15)
        # self.series.append(20, 15)
        # self.series.append(30, 15)
        # self.series.append(40, 15)
        
        # pen = QPen()
        # pen.setWidth(4)
        # self.series.setPen(pen)
        # self.series.setColor(QColor("Blue"))
        # self.chart.addSeries(self.series)
        
        # # legend
        # self.chart.legend().setAlignment(Qt.AlignRight)
        # self.chart.legend().setLabelBrush(axisBrush)
        
        # self.series.attachAxis(axis_x)
        # self.series.attachAxis(axis_y)
        
        # self.chart.setBackgroundBrush(QBrush(QColor(22,32,42)))
        # self.chart_view = QChartView(self.chart)
        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                    "ui/qchart_test.ui")
        uic.loadUi(ui_path, self)
        
        self.cur_series = QLineSeries()
        self.now = QDateTime.currentDateTime()
        self.viewLimit = 300
        
        for i in range(self.viewLimit, 1, -1):
            cur = 20 * random.random()
            time = self.now.addSecs(-i).toMSecsSinceEpoch()  #Processing to append to QLineSeries
            self.cur_series.append(time, cur)

        self.chart = QChart()
        # self.chart.setAnimationOptions(QChart.SeriesAnimations)
        
        self.chart.legend().hide()
        self.chart.addSeries(self.cur_series)
        self.font = QFont()
        self.font.setPixelSize(20)        
        self.font.setBold(3)
        self.chart.setTitle("Visibility Graph")
        self.chart.setTitleFont(self.font)
        self.chart_view = QChartView()
        self.chart_view.setChart(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        # self.chart_view.show()
        # self.verticalLayout.addWidget(self.chart_view)
        
        #Create X axis
        time_axis_x = QDateTimeAxis()
        time_axis_x.setFormat("hh:mm:ss")
        self.chart.addAxis(time_axis_x, Qt.AlignBottom)
        self.cur_series.attachAxis(time_axis_x)

        #Create Y1 axis
        cur_axis_y = QValueAxis()
        cur_axis_y.setTitleText("Visibility(km)")
        cur_axis_y.setLinePenColor(self.cur_series.pen().color())  #Make the axis and chart colors the same
        cur_axis_y.setRange(0, 20)
        self.chart.addAxis(cur_axis_y, Qt.AlignLeft)
        self.cur_series.attachAxis(cur_axis_y)

        self.pw = ValueWorker("Test")
        self.pw.dataSent.connect(self.appendData)
        self.pw.start()
        
    
    def appendData(self, value):
        if len(self.cur_series) == self.viewLimit:
            self.cur_series.remove(0)
        dt = QDateTime.currentDateTime()
        self.cur_series.append(dt.toMSecsSinceEpoch(), value)
        self.__updateAxis()
    
    def __updateAxis(self):
        pvs = self.cur_series.pointsVector()
        dtStart = QDateTime.fromMSecsSinceEpoch(int(pvs[0].x()))
        if len(self.cur_series) == self.viewLimit:
            dtLast = QDateTime.fromMSecsSinceEpoch(int(pvs[-1].x()))
        else:
            dtLast = dtStart.addSecs(self.viewLimit)
        
        ax = self.chart.axisX()
        ax.setRange(dtStart, dtLast)
        # return chart_view
        
        
               
    
    
        
        

class JS06MainWindow(QWidget):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "ui/js06_1920_new.ui")
        uic.loadUi(ui_path, self)

        self.camera_name = ""
        self.video_thread = None
        # self.ipcam_start()
        self.begin = QPoint()
        self.end = QPoint()
        self.qt_img = QPixmap()
        self.isDrawing = False
        self.curved_thread = None

        self.upper_left = ()
        self.lower_right = ()
        self.left_range = []
        self.right_range = []
        self.distance = []
        self.target_name = []
        self.min_x = []
        self.min_y = []
        self.min_xy = ()
        self.leftflag = False
        self.rightflag = False
        self.image_width = None
        self.image_height = None
        self.video_flag = False
        self.cp_image = None
        self.g_ext = None
        self.pm_25 = None
        self.test_name = None
        self.end_drawing = None
        self.radio_checked = None
        self.visibility_copy = 0
        self.running_ave_checked = None
        self.q_list = []
        self.q_list_scale = 300
        
        self.chart_view = Vis_Chart()
        
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        args = [
            "--rtsp-frame-buffer-size",
            "1000000"
        ]

        self.instance = vlc.Instance(args)
        self.instance.log_unset()
        self.media_player = self.instance.media_player_new()

        self.image_player = self.instance.media_list_player_new()
        self.image_media = self.instance.media_list_new('')

        self.video_frame = QFrame()

        if sys.platform == 'win32':
            self.media_player.set_hwnd(self.video_frame.winId())

        self.filepath = os.path.join(os.getcwd())

        # Create a QGraphicsView to show the camera image
        self.verticallayout.addWidget(self.video_frame)

        # self.webview = QtWebEngineWidgets.QWebEngineView()
        # self.webview.setUrl(QUrl("http://localhost:3000/d/GXA3xPS7z/new-dashboard-copy?orgId=1&kiosk&from=now-1h&to=now"))
        # self.webview.setZoomFactor(1)
        # self.webview.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        # self.webview.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        # self.webview.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        # self.web_verticalLayout.addWidget(self.webview)
        self.web_verticalLayout.addWidget(self.chart_view.chart_view)
        

        # # Create QMediaPlayer that plays video
  
        VIDEO_SRC3 = "rtsp://admin:sijung5520@192.168.100.132/profile2/media.smp"
        
        CAM_NAME = "PNM_9030V"
        self.onCameraChange(VIDEO_SRC3, CAM_NAME, "Video")
        
        self.settings_button.clicked.connect(self.btn_test)
        
        self.video_thread = CurveThread(VIDEO_SRC3, "Video", q)
        self.video_thread.update_visibility_signal.connect(self.print_data)
        self.video_thread.start()

        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout_run)
        
        if os.path.isdir("./path_info"):
            pass        
        else:
            save_path_info.init_data_path()       
    
    @pyqtSlot()
    def btn_test(self):
        if self.radio_checked == None:
            dlg = JS06_Setting_Widget("Km")
        else:
            dlg = JS06_Setting_Widget(self.radio_checked)
        dlg.show()
        # sys.exit(app.exec_())
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.exec_()
        
        self.radio_checked = dlg.radio_flag
        print(self.radio_checked, "변환 완료")
        
        self.running_ave_checked = dlg.running_ave_checked
        print(self.running_ave_checked, "변환 완료")
        
        if self.running_ave_checked == "One":
            self.q_list_scale = 30
        elif self.running_ave_checked == "Five":
            self.q_list_scale = 150
        elif self.running_ave_checked == "Ten":
            self.q_list_scale = 300
                
    @pyqtSlot(str)
    def print_data(self, visibility):
        print(visibility)
        visibility_float = round(float(visibility), 3)
        
        if len(self.q_list) == 0 or self.q_list_scale != len(self.q_list):
            self.q_list = []
            for i in range(self.q_list_scale):
                self.q_list.append(visibility_float)
                
            print("q 리스트 길이", len(self.q_list))
            result_vis = np.mean(self.q_list)
        else:
            print("q 리스트 길이2", len(self.q_list))
            self.q_list.pop(0)
            self.q_list.append(visibility_float)
            result_vis = np.mean(self.q_list)            
        
        self.visibility_copy = round(float(result_vis), 3)
        
        if self.radio_checked == None or self.radio_checked == "Km":
            visibility_text = str(self.visibility_copy) + " km"
            print(visibility_text)
        elif self.radio_checked == "Mile":
            visibility_mile = round(self.visibility_copy / 1.609, 1)
            print(visibility_mile)
            visibility_text = str(visibility_mile) + " mi"
        
        self.c_vis_label.setText(visibility_text)
        
        ext = 3.912 / self.visibility_copy
        hd = 89
        pm_value = round((ext*1000/4/2.5)/(1+5.67*((hd/100)**5.8)),2)
        pm_text = str(pm_value) + " ㎍/㎥"
        self.c_pm_label.setText(pm_text)
        
        self.data_storage(self.visibility_copy)
        # self.statusBar().showMessage(data)
        
    @pyqtSlot(str)
    def onCameraChange(self, url, camera_name, src_type):
        """Connect the IP camera and run the video thread."""

        if url[:4] == "rtsp":
            self.media_player.set_media(self.instance.media_new(url))
            self.media_player.video_set_aspect_ratio("11:3")
            self.media_player.play()
        else:
            pass

    def timeout_run(self):
        """Print the current time."""
        current_time = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(time.time()))
        self.real_time_label.setText(current_time)
    
    def save_frame(self, image: np.ndarray, epoch: str, g_ext, pm_25):
        """Save the image of the calculation time."""
        print("save_frame 시작")
        image_path = os.path.join(self.filepath, f"{self.test_name}")
        file_name = f"{epoch}"
        if not os.path.isdir(image_path):
            os.makedirs(image_path)

        g_ext = round(g_ext / 1000, 4)

        if not os.path.isfile(f"{image_path}/{file_name}_{g_ext}_{pm_25}.jpg"):
            cv2.imwrite(f"{image_path}/{file_name}_{g_ext}_{pm_25}.jpg", image)
            del image
            del image_path
            cv2.destroyAllWindows()
            print(file_name , "The image has been saved.")
            return

    def keyPressEvent(self, e):
        """Override function QMainwindow KeyPressEvent that works when key is pressed"""
        if e.key() == Qt.Key_Escape:
            sys.exit()
        if e.key() == Qt.Key_F:
            self.widget_toggle_flag()
        
    def widget_toggle_flag(self):
        if self.windowState() & Qt.WindowFullScreen:
            self.showNormal()
        else:
            self.showFullScreen()
        
    def data_storage(self, vis_data):
        """Store visibility and fine dust values ​​in the database."""

        save_db.SaveDB(vis_data)
        print("data storage!")

    def save_target(self):
        """Save the target information for each camera."""
        try:
            save_path = os.path.join(f"target/{self.camera_name}")
            os.makedirs(save_path)

        except Exception as e:
            pass

        if self.left_range:
            col = ["target_name", "left_range", "right_range", "distance"]
            result = pd.DataFrame(columns=col)
            result["target_name"] = self.target_name
            result["left_range"] = self.left_range
            result["right_range"] = self.right_range
            result["distance"] = self.distance
            result.to_csv(f"{save_path}/{self.camera_name}.csv", mode="w", index=False)



if __name__ == '__main__':
    
    # try:
    #     os.chdir(sys._MEIPASS)
    #     print(sys._MEIPASS)
    # except:
    #     os.chdir(os.getcwd())
    
    
    mp.freeze_support()
    q = Queue()
    p = Process(name="producer", target=video_thread_mp.producer, args=(q, ), daemon=True)
    p.start()
    
    app = QApplication(sys.argv)
    # MainWindow = QMainWindow()
    ui = JS06MainWindow()
    # tabs = QTabWidget()
    # tabs.addTab(ui, 'tab1')
    # ui2 = GraFanaMainWindow()
    # tabs.addTab(ui2, 'tab2')
    # ui.setupUi(MainWindow)
    # tabs.showFullScreen()
    # tabs.show()
    ui.show()
    # sys.exit(p)    
    sys.exit(app.exec_())
