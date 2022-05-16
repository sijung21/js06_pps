import os
import time
import random
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QImage, QPainter, QBrush, QColor, QPen, QImage, QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QVBoxLayout, QWidget, QLabel, QInputDialog, QGraphicsScene, QGraphicsView, QFrame, QTabWidget
from PyQt5.QtCore import QPoint, QRect, Qt, QRectF, QSize, QCoreApplication, pyqtSlot, QTimer, QUrl, QDateTime, pyqtSignal, QThread
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis, QScatterSeries

from influxdb import InfluxDBClient




class ValueWorker(QThread):   
    
    dataSent = pyqtSignal(float)
    
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.alive = True
        
    def run(self):
        while self.alive:
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
            time.sleep(30)
            self.dataSent.emit(data)
    
    def close(self):
        self.alive = False
        
class Vis_Chart(QWidget):
    
    def __init__(self, parent=None, max_value = 50):
        super().__init__(parent)       
                
        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                    "ui/qchart_test.ui")
        uic.loadUi(ui_path, self)
        
        self.vis_series = QLineSeries()
        self.vis_scatter = QScatterSeries()
        self.vis_scatter_2 = QScatterSeries()
        pen = QPen(QColor(32,159,223))        
        pen.setWidth(3)

        self.vis_series.setPen(pen)
        self.vis_scatter.setBorderColor(QColor(32,159,223))
        self.vis_scatter.setBrush(QColor(32,159,223))
        
        self.vis_scatter_2.setMarkerSize(8)
        self.vis_scatter_2.setBorderColor(QColor(225,225,225))
        self.vis_scatter_2.setBrush(QColor(225,225,225))
        
        self.vis_series.setName("Visibility")
        self.vis_series.setPointsVisible()
        self.now = QDateTime.currentDateTime()
        self.viewLimit = 600
        self.timetick = 30
        for i in range(self.viewLimit, 1, -self.timetick):
            cur = 20 * random.random()
            time = self.now.addSecs(-i).toMSecsSinceEpoch()  #Processing to append to QLineSeries
            self.vis_series.append(time, cur)
            self.vis_scatter.append(time, cur)
            self.vis_scatter_2.append(time, cur)

        self.chart = QChart()
        # self.chart.setAnimationOptions(QChart.SeriesAnimations)
        
        self.chart.legend().hide()
        self.chart.addSeries(self.vis_series)
        self.chart.addSeries(self.vis_scatter)
        self.chart.addSeries(self.vis_scatter_2)
        self.font = QFont()
        self.font.setPixelSize(20)        
        self.font.setBold(3)
        self.chart.setTitle("Visibility Graph")
        self.chart.setTitleFont(self.font)
        self.chart.setTitleBrush(QBrush(QColor("white")))
        self.chart.layout().setContentsMargins(0,0,0,0)
        self.chart.setBackgroundRoundness(0)
        self.chart.setBackgroundBrush(QBrush(QColor(22,32,42)))

        self.chart_view = QChartView()
        self.chart_view.setChart(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        axisBrush = QBrush(QColor("white"))

        #Create X axis
        time_axis_x = QDateTimeAxis()
        time_axis_x.setFormat("hh:mm:ss")
        time_axis_x.setTitleText("Time")
        time_axis_x.setTitleBrush(axisBrush)
        time_axis_x.setLabelsBrush(axisBrush)
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
        self.chart.addAxis(cur_axis_y, Qt.AlignLeft)
        self.vis_series.attachAxis(cur_axis_y)
        self.vis_scatter.attachAxis(cur_axis_y)
        self.vis_scatter_2.attachAxis(cur_axis_y)

        self.pw = ValueWorker("Test")
        self.pw.dataSent.connect(self.appendData)
        self.pw.start()
        
    
    def appendData(self, value):
        if len(self.vis_series) == (self.viewLimit//self.timetick):
            self.vis_series.remove(0)
            self.vis_scatter.remove(0)
            self.vis_scatter_2.remove(0)
        dt = QDateTime.currentDateTime()
        self.vis_series.append(dt.toMSecsSinceEpoch(), value)
        self.vis_scatter.append(dt.toMSecsSinceEpoch(), value)
        self.vis_scatter_2.append(dt.toMSecsSinceEpoch(), value)
        self.__updateAxis()
    
    def __updateAxis(self):
        pvs = self.vis_series.pointsVector()
        dtStart = QDateTime.fromMSecsSinceEpoch(int(pvs[0].x()))
        if len(self.vis_series) == self.viewLimit:
            dtLast = QDateTime.fromMSecsSinceEpoch(int(pvs[-1].x()))
        else:
            dtLast = dtStart.addSecs(self.viewLimit)
        
        ax = self.chart.axisX()
        ax.setRange(dtStart, dtLast)
        # return chart_view