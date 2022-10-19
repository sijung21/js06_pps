import os
import time
import random
from PyQt5.QtGui import QPixmap, QImage, QPainter, QBrush, QColor, QPen, QImage, QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QVBoxLayout, QWidget, QLabel, QInputDialog, QGraphicsScene, QGraphicsView, QFrame, QTabWidget
from PyQt5.QtCore import QPoint, QRect, Qt, QRectF, QSize, QCoreApplication, pyqtSlot, QTimer, QUrl, QDateTime, pyqtSignal, QThread
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis, QScatterSeries

from influxdb import InfluxDBClient
import js06_log

class ValueWorker(QThread):   
    """Influx에 저장된 시정 값을 읽어 실시간 시정 출력 그래프에 전송하는 QThread 클래스"""
    dataSent = pyqtSignal(float)
    
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.alive = True
        self.logger = js06_log.CreateLogger(__name__)
        
        
    def run(self):
        
        data = None
        
        while self.alive:
            # InfluxDB에 접속
            client = InfluxDBClient('localhost', 8086)
            save_time = time.time_ns()
            
            try:        
                client.create_database("Sijung")
                self.logger.info("Create Sijung Database")
            except TypeError as e:        
                print(e)
                print("create except")                
                pass
            
            client.switch_database("Sijung")
            
            
            
            # 최근에 저장된 시정을 조회하는 쿼리문
            query = 'SELECT "visbility" FROM "JS06" ORDER BY "time" DESC LIMIT 1'
            result = client.query(query)
            visiblity = result.get_points()
            # 쿼리 조회 결과문에서 시정 값만 추출 및 저장
            for item in list(visiblity):
                data = item['visbility']
                
            client.close()
            if data is not None:
                # QThread를 선언한 곳에 전송
                self.dataSent.emit(data)
                self.logger.info("Complete transfer of values to Visiblity chart")
            else:
                self.dataSent.emit(0)
            # 30초마다 실행
            # time.sleep(30)
            
    
    def close(self):
        self.alive = False
        
class Vis_Chart(QWidget):
    """ 실시간 시정 출력 그래프 위젯 """
    
    # 초기화 선언
    def __init__(self, parent=None, max_value = 50):
        super().__init__(parent) 
        
        # chart에 넣을 Series 선언
        self.vis_series = QLineSeries() # 직선 Series
        self.vis_scatter = QScatterSeries() # 파란 산점도 Series
        self.vis_scatter_2 = QScatterSeries() # 하얀 산점도 Series
        
        # 직선 Series에 입힐 색과 두께 설정
        pen = QPen(QColor(32,159,223))        
        pen.setWidth(3)
        self.vis_series.setPen(pen)
        
        # 산점도 Series들의 색상과 두께 설정
        self.vis_scatter.setBorderColor(QColor(32,159,223))
        self.vis_scatter.setBrush(QColor(32,159,223))
        
        self.vis_scatter_2.setMarkerSize(8)
        self.vis_scatter_2.setBorderColor(QColor(225,225,225))
        self.vis_scatter_2.setBrush(QColor(225,225,225))
        
        # 현재 시간 저장
        self.now = QDateTime.currentDateTime()
        # 몇초 전까지 보여주는지 설정 값
        self.viewLimit = 1800
        # 몇초 단위로 저장하는지 설정
        self.timetick = 60
        # 각 Series에 랜덤으로 몇초 전까지의 데이터들을 임의로 저장 
        for i in range(self.viewLimit, 1, -self.timetick):
            # cur = 20 * random.random()
            time = self.now.addSecs(-i).toMSecsSinceEpoch()  #Processing to append to QLineSeries
            self.vis_series.append(time, 0)
            self.vis_scatter.append(time, 0)
            self.vis_scatter_2.append(time, 0)

        # Seires를 담을 Qchart를 선언
        self.chart = QChart()
        
        # 그래프 그릴 때 애니메이션 효과 적용
        # self.chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Qchart에 Series들 추가
        self.chart.addSeries(self.vis_series)
        self.chart.addSeries(self.vis_scatter)
        self.chart.addSeries(self.vis_scatter_2)
        
        # Qchart 설정
        self.chart.legend().hide()        
        # # Qchart의 타이틀 글자 색, 크기 설정 
        self.font = QFont()
        self.font.setPixelSize(20)        
        self.font.setBold(3)
        self.chart.setTitle("Visibility Graph")
        self.chart.setTitleFont(self.font)
        self.chart.setTitleBrush(QBrush(QColor("white")))
        # Qchart 여백 제거
        self.chart.layout().setContentsMargins(0,0,0,0)
        # Qchart 테두리 라운드 제거
        self.chart.setBackgroundRoundness(0)
        # Qchart 배경색 지정
        self.chart.setBackgroundBrush(QBrush(QColor(22,32,42)))

        
        # ChartView 선언
        self.chart_view = QChartView()
        # ChartView에 Qchart를 탑재
        self.chart_view.setChart(self.chart)
        # ChartView 안에 있는 내용(차트, 글자 등)들을 부드럽게 해주는 설정
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        # x,y 축의 글자 색 지정
        axisBrush = QBrush(QColor("white"))

        #Create X axis
        time_axis_x = QDateTimeAxis()
        time_axis_x.setFormat("hh:mm:ss")
        time_axis_x.setTitleText("Time")
        time_axis_x.setTitleBrush(axisBrush)
        time_axis_x.setLabelsBrush(axisBrush)
        time_axis_x.setTickCount(7)
        self.chart.addAxis(time_axis_x, Qt.AlignBottom)

        self.vis_series.attachAxis(time_axis_x)
        self.vis_scatter.attachAxis(time_axis_x)
        self.vis_scatter_2.attachAxis(time_axis_x)

        #Create Y1 axis
        cur_axis_y = QValueAxis()
        cur_axis_y.setTitleText("Visibility(km)")
        cur_axis_y.setLinePenColor(self.vis_series.pen().color())  #Make the axis and chart colors the same
        cur_axis_y.setTitleBrush(axisBrush)
        cur_axis_y.setLabelsBrush(axisBrush)
        cur_axis_y.setRange(0, 25)
        cur_axis_y.setTickCount(6)
        self.chart.addAxis(cur_axis_y, Qt.AlignLeft)
        self.vis_series.attachAxis(cur_axis_y)
        self.vis_scatter.attachAxis(cur_axis_y)
        self.vis_scatter_2.attachAxis(cur_axis_y)

        # 새로운 데이터를 계속 호출하는 QThread 클래스 선언
        # self.pw = ValueWorker("Test")
        # 전송 받은 시정 값을 appendData 함수의 value 인자값에 직접 전달
        # self.pw.dataSent.connect(self.appendData)
        # QThread 시작
        # self.pw.start()
        
        self.logger = js06_log.CreateLogger(__name__)
        self.logger.info("Success drawing the visibility chart")
        
    
    def appendData(self, value):
        """ Series에 가장 오래된 데이터를 지우고 새로운 데이터를 추가하는 함수 """
        if len(self.vis_series) == (self.viewLimit//self.timetick):
            self.vis_series.remove(0)
            self.vis_scatter.remove(0)
            self.vis_scatter_2.remove(0)
        dt = QDateTime.currentDateTime()
        print("QDate time",dt)
        self.vis_series.append(dt.toMSecsSinceEpoch(), value)
        self.vis_scatter.append(dt.toMSecsSinceEpoch(), value)
        self.vis_scatter_2.append(dt.toMSecsSinceEpoch(), value)
        self.__updateAxis()
    
    def __updateAxis(self):
        """ Qchart의 X축의 범위를 재지정하는 함수 """
        pvs = self.vis_series.pointsVector()
        dtStart = QDateTime.fromMSecsSinceEpoch(int(pvs[0].x()))
        if len(self.vis_series) == self.viewLimit:
            dtLast = QDateTime.fromMSecsSinceEpoch(int(pvs[-1].x()))
        else:
            dtLast = dtStart.addSecs(self.viewLimit)
        print("qchart recent time : ", dtLast)
        ax = self.chart.axisX()
        ax.setRange(dtStart, dtLast)
        # return chart_view