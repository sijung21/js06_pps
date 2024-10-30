
import datetime
import sys
import os
import time
import math

import cv2
import numpy as np
import pandas as pd
import scipy
from scipy.optimize import curve_fit
# import PyQt5
# print(PyQt5.__version__)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QBrush, QColor, QPen, QImage, QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QVBoxLayout, QWidget, QLabel, QInputDialog, QDialog, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox
from PyQt5.QtCore import QPoint, QRect, Qt, QRectF, QSize, QCoreApplication, pyqtSlot, QTimer, QUrl
from PyQt5 import uic

from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis

import target_info
import save_path_info

import js06_log

class JS06_Setting_Widget(QDialog):

    def __init__(self, radio_flag=None, *args, **kwargs):

        super().__init__(*args, **kwargs)
        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "ui/js06_settings.ui")
        uic.loadUi(ui_path, self)
        appIcon = QIcon('logo.png')
        self.setWindowIcon(appIcon)
        
        self.begin = QPoint()
        self.end = QPoint()
        self.qt_img = QPixmap()
        self.isDrawing = False
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
        self.r_list = []
        self.g_list = []
        self.b_list = []
        self.x = None
        self.chart_view = None
        self.rtsp_path = None
        self.logger = js06_log.CreateLogger(__name__)
        self.logger.info('Setup window initialization complete')
        
        # self.running_ave_checked = run_ave_flag
        run_ave = save_path_info.get_data_path('SETTING','running_average')
        
        self.radio_flag = radio_flag
        
        self.cal_radio_flag = save_path_info.get_data_path('Method', 'method')
        
        data_path_text = save_path_info.get_data_path('Path', 'data_csv_path')
        
        self.data_path_textEdit.setPlainText(data_path_text)
        
        image_path_text = save_path_info.get_data_path('Path','image_save_path')
        
        self.image_path_textEdit.setPlainText(image_path_text)
        
        log_path_text = save_path_info.get_data_path('Path','log_path')
        
        self.log_path_textEdit.setPlainText(log_path_text)
        
        self.rtsp_path = save_path_info.get_data_path('SETTING','camera_ip')
        
        cam_name = save_path_info.get_data_path('SETTING','camera_name')
        
        self.image_load()        
        
        # 그림 그리는 Q레이블 생성
        self.blank_lbl = QLabel(self.target_setting_image_label)
        self.blank_lbl.setGeometry(0, 0, 1200, 500)
        self.blank_lbl.paintEvent = self.lbl_paintEvent

        self.blank_lbl.mousePressEvent = self.lbl_mousePressEvent
        self.blank_lbl.mouseMoveEvent = self.lbl_mouseMoveEvent
        self.blank_lbl.mouseReleaseEvent = self.lbl_mouseReleaseEvent
        
        if self.radio_flag == None or self.radio_flag == "Km":
            self.km_radio_btn.setChecked(True)
        elif self.radio_flag == "Mile":
            self.mile_radio_btn.setChecked(True)
        
        if self.cal_radio_flag == None or self.cal_radio_flag == "EXT":
            self.ext_radio_btn.setChecked(True)
        elif self.cal_radio_flag == "AI":
            self.ai_radio_btn.setChecked(True)
        
        self.target_name, self.left_range, self.right_range, self.distance = target_info.get_target(cam_name)
    
        if run_ave == "10":
            self.ten_radio_btn.setChecked(True)
        elif run_ave == "5":
            self.five_radio_btn.setChecked(True)
        else:
            self.one_radio_btn.setChecked(True)
        
        self.red_checkBox.setChecked(True)
        self.green_checkBox.setChecked(True)
        self.blue_checkBox.setChecked(True)
        
        if len(self.left_range) > 0:
            self.show_target_table()
        else:
            pass
        
        if len(self.left_range) > 4:
            self.chart_update()
        else:
            pass
        
        
        
        self.data_path_pbtn.clicked.connect(self.data_path_folder_open)
        self.image_path_pbtn.clicked.connect(self.image_path_folder_open)
        self.log_path_pbtn.clicked.connect(self.log_path_folder_open)
        
        ## 라디오 버튼, 체크박스 이벤트시 함수와 연동 설정
        
        self.km_radio_btn.clicked.connect(self.radio_function)
        self.mile_radio_btn.clicked.connect(self.radio_function)  
        
        self.ai_radio_btn.clicked.connect(self.cal_radio_function)
        self.ext_radio_btn.clicked.connect(self.cal_radio_function)  
        
        self.red_checkBox.clicked.connect(self.chart_update)
        self.green_checkBox.clicked.connect(self.chart_update)
        self.blue_checkBox.clicked.connect(self.chart_update)
        
        self.one_radio_btn.clicked.connect(self.running_avr_time_settings_function)
        self.five_radio_btn.clicked.connect(self.running_avr_time_settings_function)
        self.ten_radio_btn.clicked.connect(self.running_avr_time_settings_function)
    

    # path_setting
    def data_path_folder_open(self):
        folder = None
        
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder is not None and len(folder) > 0:
            self.data_path_textEdit.clear()
            self.data_path_textEdit.setPlainText(folder)
            save_path_info.set_data_path('data_path', folder)
        else:
            pass
            
    def image_path_folder_open(self):
        folder = None
        
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        
        if folder is not None and len(folder) > 0:
            self.image_path_textEdit.clear()
            self.image_path_textEdit.setPlainText(folder)
            save_path_info.set_data_path('image_path', folder)
        else:
            pass
            
    def log_path_folder_open(self):
        folder = None
        
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        
        if folder is not None and len(folder) > 0:
            self.log_path_textEdit.clear()
            self.log_path_textEdit.setPlainText(folder)
            save_path_info.set_data_path('log_path', folder)        
        else:
            pass
            
    def func(self, x, c1, c2, a):
        return c2 + (c1 - c2) * np.exp(-a * x)    
    
    def chart_update(self):
        """세팅창 그래프를 업데이트 하는 함수"""
        
        if len(self.left_range) < 4:
            print("Target을 추가해주세요")
            self.no_graph_label.show()
            return
        else:
            self.no_graph_label.hide()
            pass
            
        if self.html_verticalLayout.count() == 0:
            self.chart_view = self.chart_draw()
            self.html_verticalLayout.addWidget(self.chart_view)        
        else:
            new_chart_view = self.chart_draw()
            self.html_verticalLayout.removeWidget(self.chart_view)
            self.html_verticalLayout.addWidget(new_chart_view)            
            self.html_verticalLayout.update()
            self.chart_view = new_chart_view
            
        print("update chart!")
        self.logger.info('update chart!')
        
    def chart_draw(self):
        """세팅창 그래프 칸에 소산계수 차트를 그리는 함수"""
        # data
        global x   
        
        # if self.x is None:
        self.logger.debug(f'distance list : {str(self.distance)}')
        print("distance 리스트", self.distance)
        
        self.x = np.linspace(self.distance[0], self.distance[-1], 100, endpoint=True)
        self.x.sort()
        
        hanhwa_opt_r, hanhwa_cov_r = curve_fit(self.func, self.distance, self.r_list, maxfev=5000)
        hanhwa_opt_g, hanhwa_cov_g = curve_fit(self.func, self.distance, self.g_list, maxfev=5000)
        hanhwa_opt_b, hanhwa_cov_b = curve_fit(self.func, self.distance, self.b_list, maxfev=5000)
        
        # chart object
        chart = QChart()
        font = QFont()
        font.setPixelSize(20)        
        font.setBold(3)
        chart.setTitleFont(font)
        chart.setTitleBrush(QBrush(QColor("white")))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.layout().setContentsMargins(0,0,0,0)
        chart.setBackgroundRoundness(0)
        
        
        chart.setTitle('Extinction coefficient Graph')
        
        axisBrush = QBrush(QColor("white"))
        
        # chart.createDefaultAxes()
        axis_x = QValueAxis()
        axis_x.setTickCount(7)
        axis_x.setLabelFormat("%i")
        axis_x.setTitleText("Distance(km)")
        axis_x.setRange(0,50)        
        axis_x.setLabelsBrush(axisBrush)
        axis_x.setTitleBrush(axisBrush)     
        chart.addAxis(axis_x, Qt.AlignBottom)        
        
        axis_y = QValueAxis()
        axis_y.setTickCount(7)
        axis_y.setLabelFormat("%i")
        axis_y.setTitleText("Intensity")
        axis_y.setRange(0, 255)
        axis_y.setLabelsBrush(axisBrush)
        axis_y.setTitleBrush(axisBrush)           
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        # Red Graph
        if self.red_checkBox.isChecked():
        
            series1 = QLineSeries()
            series1.setName("Red")
            pen = QPen()
            pen.setWidth(4)
            series1.setPen(pen)
            series1.setColor(QColor("Red"))
            
            for dis in self.x:
                series1.append(*(dis, self.func(dis, *hanhwa_opt_r)))
            chart.addSeries(series1) # data feeding  
            series1.attachAxis(axis_x)
            series1.attachAxis(axis_y)
        
        # Green Graph
        if self.green_checkBox.isChecked():
        
            series2 = QLineSeries()
            series2.setName("Green")
            pen = QPen()
            pen.setWidth(4)
            series2.setPen(pen)   
            series2.setColor(QColor("Green")) 
            for dis in self.x:
                series2.append(*(dis, self.func(dis, *hanhwa_opt_g)))
            chart.addSeries(series2)  # data feeding
            
            series2.attachAxis(axis_x)
            series2.attachAxis(axis_y)  
            

        # Blue Graph
        if self.blue_checkBox.isChecked():
            series3 = QLineSeries()
            series3.setName("Blue")  
            pen = QPen()
            pen.setWidth(4)
            series3.setPen(pen)   
            series3.setColor(QColor("Blue"))
            for dis in self.x:
                series3.append(*(dis, self.func(dis, *hanhwa_opt_b)))
            chart.addSeries(series3)  # data feeding
            
            series3.attachAxis(axis_x)
            series3.attachAxis(axis_y) 
        
        # legend
        chart.legend().setAlignment(Qt.AlignRight)
        chart.legend().setLabelBrush(axisBrush)
        
        # displaying chart
        chart.setBackgroundBrush(QBrush(QColor(22,32,42)))
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view
    
    def running_avr_time_settings_function(self):
        """radio button 설정에 따라 Running Average 단위를 변경해서 설정하는 함수"""
        if self.one_radio_btn.isChecked():
            # self.running_ave_checked = "One"
            save_path_info.set_data_path("SETTING", "running_average", "1")
            
        elif self.five_radio_btn.isChecked():
            # self.running_ave_checked = "Five"
            save_path_info.set_data_path("SETTING", "running_average", "5")
            
        elif self.ten_radio_btn.isChecked():
            # self.running_ave_checked = "Ten"
            save_path_info.set_data_path("SETTING", "running_average", "10")

    def radio_function(self):
        """radio button 설정에 따라 시정 단위를 변경해서 출력하는 함수"""
        if self.km_radio_btn.isChecked():
            self.radio_flag = "Km"
            
            # print(self.radio_flag)
        elif self.mile_radio_btn.isChecked():
            self.radio_flag = "Mile"
            # print(self.radio_flag)
    
    def cal_radio_function(self):
        """radio button 설정에 따라 계산 방법을 변경하는 함수"""
        if self.ai_radio_btn.isChecked():
            self.cal_radio_flag = "AI"
            save_path_info.set_data_path("Method", "method", "AI")
        elif self.ext_radio_btn.isChecked():
            self.cal_radio_flag = "EXT"
            save_path_info.set_data_path("Method", "method", "EXT")
        
    def image_load(self):
        
        cam_id = save_path_info.get_data_path("SETTING", "camera_id")
        cam_pwd = save_path_info.get_data_path("SETTING", "camera_pw")
        save_profile = save_path_info.get_data_path("SETTING", "save_profile")
        
        src = f"rtsp://{cam_id}:{cam_pwd}@{self.rtsp_path}/{save_profile}/media.smp" 
        # src = "C:/Users/user/Workspace/water_gauge/src/video_files/daejeon_1.mp4"
        try:
            cap = cv2.VideoCapture(src)
            ret, cv_img = cap.read()
            cp_image = cv_img.copy()
            cap.release()
        except Exception as e:
            print(e)
            self.image_load()
            
        self.target_setting_image_label.setPixmap(self.convert_cv_qt(cp_image))
        
    def convert_cv_qt(self, cv_img):
        """Convert CV image to QImage."""
        # self.epoch = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        cv_img = cv_img.copy()
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        self.cp_image = cv_img.copy()        
        img_height, img_width, ch = cv_img.shape
        self.image_width = int(img_width)
        self.image_height = int(img_height)
        # self.video_flag = True
        bytes_per_line = ch * img_width
        convert_to_Qt_format = QImage(cv_img.data, img_width, img_height, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(1200, 500, Qt.KeepAspectRatio,
                                    Qt.SmoothTransformation)
        return QPixmap.fromImage(p)
    
    
    def lbl_paintEvent(self, event):
        self.horizontal_flag = True
        painter = QPainter(self.blank_lbl)

        # if self.camera_name == "Image" and self.video_flag:
        back_ground_image =  self.thumbnail(self.cp_image)
        bk_image = QPixmap.fromImage(back_ground_image)
        painter.drawPixmap(QRect(0, 0, 1200, 500), bk_image)

        # if self.horizontal_flag and self.video_flag:
        for corner1, corner2, in zip(self.left_range, self.right_range):
            br = QBrush(QColor(100, 10, 10, 40))
            painter.setBrush(br)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            corner1_1 = int(corner1[0]/self.image_width*self.blank_lbl.width())
            corner1_2 = int(corner1[1]/self.image_height*self.blank_lbl.height())
            corner2_1 = int((corner2[0]-corner1[0])/self.image_width*self.blank_lbl.width())
            corner2_2 = int((corner2[1]-corner1[1])/self.image_height*self.blank_lbl.height())
            painter.drawRect(QRect(corner1_1, corner1_2, corner2_1, corner2_2))
        
        if self.isDrawing:
            br = QBrush(QColor(100, 10, 10, 40))
            painter.setBrush(br)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.drawRect(QRect(self.begin, self.end))
            # 썸네일 만들기
            th_x, th_y = self.thumbnail_pos(self.end)
            th_qimage = self.thumbnail(self.cp_image[th_y - 50 :th_y + 50, th_x - 50 :th_x + 50, :])
            thumbnail_image = QPixmap.fromImage(th_qimage)
            painter.drawPixmap(QRect(self.end.x(), self.end.y(), 200, 200), thumbnail_image)

        if self.end_drawing:
            # print("썸네일 삭제")
            painter.eraseRect(QRect(self.begin, self.end))
            painter.eraseRect(QRect(self.end.x(), self.end.y(), 200, 200))
            self.end_drawing = False
            self.isDrawing = False
            self.blank_lbl.update()
        painter.end()
            
    def str_to_tuple(self, before_list):
        """저장된 타겟들의 위치정보인 튜플 리스트가 문자열로 바뀌어 다시 튜플형태로 변환하는 함수"""
        tuple_list = [i.split(',') for i in before_list]
        tuple_list = [(int(i[0][1:]), int(i[1][:-1])) for i in tuple_list]
        return tuple_list
    
    # 타겟 조정 및 썸네일 관련 함수 시작
    def thumbnail_pos(self, end_pos):
        x = int((end_pos.x()/self.blank_lbl.width())*self.image_width)
        y = int((end_pos.y()/self.blank_lbl.height())*self.image_height)
        return x, y

    def thumbnail(self, image):
        height, width, channel = image.shape
        bytesPerLine = channel * width
        qImg = QImage(image.data.tobytes(), width, height, bytesPerLine, QImage.Format_RGB888)
        return qImg

    def lbl_mousePressEvent(self, event):
        """마우스 클릭시 발생하는 이벤트, QLabel method overriding"""

        # 좌 클릭시 실행
        if event.buttons() == Qt.LeftButton:
            self.isDrawing = True
            self.begin = event.pos()
            self.end = event.pos()
            self.upper_left = (int((self.begin.x()/self.blank_lbl.width())*self.image_width),
                               int((self.begin.y()/self.blank_lbl.height())*self.image_height))
            self.blank_lbl.update()

            self.leftflag = True
            self.rightflag = False

        # 우 클릭시 실행
        elif event.buttons() == Qt.RightButton:
            self.isDrawing = False            
            self.rightflag = True
            self.leftflag = False
            
            

    def lbl_mouseMoveEvent(self, event):
        """마우스가 움직일 때 발생하는 이벤트, QLabel method overriding"""
        if event.buttons() == Qt.LeftButton:
            self.end = event.pos()
            self.blank_lbl.update()
            self.isDrawing = True

    def lbl_mouseReleaseEvent(self, event):
        """마우스 클릭이 떼질 때 발생하는 이벤트, QLabel method overriding"""
        if self.leftflag == True:
            self.end = event.pos()
            self.blank_lbl.update()
            self.lower_right = (int((self.end.x()/self.blank_lbl.width())*self.image_width),
                                int((self.end.y()/self.blank_lbl.height())*self.image_height))
            text, ok = QInputDialog.getText(self, '거리 입력', '거리(km)')
            if ok and len(text) > 0:
                try:
                    distance = float(text)
                except Exception as e:
                    QMessageBox.warning(self, 'Error', '거리를 다시 입력해주세요')
                    self.isDrawing = False
                    self.blank_lbl.update()
                    return
                self.left_range.append(self.upper_left)
                self.right_range.append(self.lower_right)
                self.distance.append(distance)
                self.target_name.append("target_" + str(len(self.left_range)))
                self.save_target()
                self.isDrawing = False
                self.end_drawing = True
                self.show_target_table()
                self.logger.info(f'Add target')
            else:
                self.isDrawing = False
                self.blank_lbl.update()
            
            if len(self.left_range) > 4:
                self.chart_update()
        else:
            if len(self.left_range) > 0:
                text, ok = QInputDialog.getText(self, '타겟 제거', '제거할 타겟 번호 입력')                
                if ok and len(text) > 0:
                    try:
                        target_num = int(text)
                    except Exception as e:
                        QMessageBox.warning(self, 'Error', '타겟 번호를 다시 입력해주세요')
                        self.isDrawing = False
                        self.blank_lbl.update()
                        return
                    
                    rm_target_name = "target_" + text
                    
                    if rm_target_name in self.target_name:                    
                        print(self.target_name)
                        del self.distance[self.target_name.index(rm_target_name)]                    
                        del self.left_range[self.target_name.index(rm_target_name)]
                        del self.right_range[self.target_name.index(rm_target_name)]
                        del self.target_name[self.target_name.index(rm_target_name)]
                        self.logger.info(f'Delete target num : {text}')
                    else:
                        QMessageBox.warning(self, 'Error', '잘못된 타겟번호입니다.')
                self.save_target()
                self.show_target_table()
                self.blank_lbl.update()
                
                if len(self.left_range) > 4:
                    self.chart_update()
    
    def save_target(self):
        """Save the target information for each camera."""
        try:
            camera_name = save_path_info.get_data_path('SETTING', 'camera_name')
            target_path = save_path_info.get_data_path('Path', 'target_csv_path')
            save_path = os.path.join(target_path, camera_name)
            os.makedirs(save_path)
            

        except Exception as e:
            pass
        
        
        print("target : ", self.target_name)
        if self.left_range:
            col = ["target_name", "left_range", "right_range", "distance"]
            result = pd.DataFrame(columns=col)
            result["target_name"] = self.target_name
            result["left_range"] = self.left_range
            result["right_range"] = self.right_range
            result["distance"] = self.distance
            result.to_csv(f"{save_path}/{camera_name}.csv", mode="w", index=False)
            self.target_name, self.left_range, self.right_range, self.distance = target_info.get_target(camera_name)
            self.logger.info(f'Save target information')
            
        else:
            col = ["target_name", "left_range", "right_range", "distance"]
            result = pd.DataFrame(columns=col)
            result.to_csv(f"{save_path}/{camera_name}.csv", mode="w", index=False)
    
    def show_target_table(self):
        """ Target의 정보들을 테이블로 보여준다 """
        
        if len(self.left_range) > 0:
            self.no_target_label.hide()
        else:
            self.no_target_label.show()
            
        min_x = []
        min_y = []
        self.r_list = []
        self.g_list = []
        self.b_list = []
        
        
        copy_image = self.cp_image.copy()
        row_count = len(self.distance)
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)        
        
        for upper_left, lower_right in zip(self.left_range, self.right_range):
            result = target_info.minrgb(upper_left, lower_right, copy_image)
            min_x.append(result[0])
            min_y.append(result[1])
            
            self.r_list.append(copy_image[result[1],result[0],0])
            self.g_list.append(copy_image[result[1],result[0],1])
            self.b_list.append(copy_image[result[1],result[0],2])
            
        for i in range(0, row_count):
            
            # 이미지 넣기            
            crop_image = copy_image[min_y[i] - 50: min_y[i] + 50, min_x[i] - 50: min_x[i] + 50, :].copy()
            cv2.rectangle(crop_image, (40, 40), (60, 60), (127, 0, 255), 2)
            item1 = self.getImagelabel(crop_image)
            self.tableWidget.setCellWidget(i, 0, item1)

            # target 번호 넣기
            item2 = QTableWidgetItem(f"Target_{i+1}")
            item2.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            item2.setForeground(QBrush(QColor(255, 255, 255)))
            self.tableWidget.setItem(i, 1, item2)
            
            # target 거리 넣기            
            item3 = QTableWidgetItem(f"{self.distance[i]}km")
            item3.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            item3.setForeground(QBrush(QColor(255, 255, 255)))
            self.tableWidget.setItem(i, 2, item3)
            
        self.logger.info(f'Show target table')
        self.tableWidget.verticalHeader().setDefaultSectionSize(90)
    
    def getImagelabel(self, image):
        """tableWidget의 셀 안에 넣을 이미지 레이블을 만드는 함수"""
        imageLabel_1 = QLabel()
        imageLabel_1.setScaledContents(True)
        height, width, channel = image.shape
        bytesPerLine = channel * width
        
        # 레이블에 이미지를 넣는다    
        qImg = QImage(image.data.tobytes(), 100, 100, bytesPerLine, QImage.Format_RGB888)
        # pixmap = QPixmap()
        
        imageLabel_1.setPixmap(QPixmap.fromImage(qImg))
        return imageLabel_1

    def no_data_print():
        return

    def closeEvent(self, QCloseEvent):
        self.deleteLater()
        print("Enter CloseEvent")
        QCloseEvent.accept()
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # MainWindow = QMainWindow()
    ui = JS06_Setting_Widget()
    # ui.setupUi(MainWindow)
    ui.show()
    sys.exit(app.exec_())

