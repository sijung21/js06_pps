import random
import sys
import os
import time
from PyQt5.QtChart import (QChart,
                           QChartView,
                           QLineSeries,
                           QValueAxis,
                           QDateTimeAxis)
from PyQt5.QtCore import (QDateTime,
                          Qt, QThread, pyqtSignal)
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import uic
from multiprocessing import Process, Queue
import multiprocessing as mp


class ValueWorker(QThread):
    dataSent = pyqtSignal(float)
    
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.alive = True
        
    def run(self):
        while self.alive:
            data = 5*random.random()
            time.sleep(10)
            self.dataSent.emit(data)
    
    def close(self):
        self.alive = False
        


class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        "ui/qchart_test.ui")
        uic.loadUi(ui_path, self)
        
        self.cur_series = QLineSeries()
        self.vol_series = QLineSeries()
        self.now = QDateTime.currentDateTime()
        self.viewLimit = 100
        
        for i in range(100, 1, -1):
            cur = 5 * random.random()
            vol = 20 * random.random()
            time = self.now.addSecs(-i).toMSecsSinceEpoch()  #Processing to append to QLineSeries
            self.cur_series.append(time, cur)
            self.vol_series.append(time, vol)

        self.chart = QChart()
        # self.chart.setAnimationOptions(QChart.SeriesAnimations)
        
        self.chart.legend().hide()
        self.chart.addSeries(self.cur_series)
        self.chart.addSeries(self.vol_series)
        self.chart_view = QChartView()
        self.chart_view.setChart(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        # self.chart_view.show()
        self.verticalLayout.addWidget(self.chart_view)
        
        #Create X axis
        time_axis_x = QDateTimeAxis()
        time_axis_x.setFormat("hh:mm:ss")
        self.chart.addAxis(time_axis_x, Qt.AlignBottom)
        self.cur_series.attachAxis(time_axis_x)
        self.vol_series.attachAxis(time_axis_x)

        #Create Y1 axis
        cur_axis_y = QValueAxis()
        cur_axis_y.setTitleText("Current[A]")
        cur_axis_y.setLinePenColor(self.cur_series.pen().color())  #Make the axis and chart colors the same
        cur_axis_y.setRange(0, 5)
        self.chart.addAxis(cur_axis_y, Qt.AlignLeft)
        self.cur_series.attachAxis(cur_axis_y)

        #Create Y2 axis
        vol_axis_y = QValueAxis()
        vol_axis_y.setTitleText("Voltage[V]")
        vol_axis_y.setLinePenColor(self.vol_series.pen().color())  #Make the axis and chart colors the same
        vol_axis_y.setRange(0, 20)
        self.chart.addAxis(vol_axis_y, Qt.AlignRight)
        self.vol_series.attachAxis(vol_axis_y)
        
        self.pw = ValueWorker("Test")
        self.pw.dataSent.connect(self.appendData)
        self.pw.start()

    def appendData(self, value):
        if len(self.cur_series) == self.viewLimit:
            self.cur_series.remove(0)
            self.vol_series.remove(0)
        
        dt = QDateTime.currentDateTime()
        self.cur_series.append(dt.toMSecsSinceEpoch(), value)
        self.vol_series.append(dt.toMSecsSinceEpoch(), 4*value)
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
        
        
        

if __name__ == "__main__":

    app = QApplication(sys.argv)
    cw = ChartWidget()
    cw.show()
    sys.exit(app.exec_())













# def keyPressEvent(e):
#     """Override function QMainwindow KeyPressEvent that works when key is pressed"""
#     if e.key() == Qt.Key_Escape:
#         sys.exit()
        
# app = QApplication(sys.argv)


# #Create appropriate data
# for i in range(100, 1, -1):
#     cur = 5 * random.random()
#     vol = 20 * random.random()
#     time = now.addSecs(-i).toMSecsSinceEpoch()  #Processing to append to QLineSeries
#     cur_series.append(time, cur)
#     vol_series.append(time, vol)

# chart = QChart()
# chart.setAnimationOptions(QChart.SeriesAnimations)
# chart.legend().hide()
# chart.addSeries(cur_series)
# chart.addSeries(vol_series)

# #Create X axis
# time_axis_x = QDateTimeAxis()
# time_axis_x.setFormat("hh:mm:ss")
# chart.addAxis(time_axis_x, Qt.AlignBottom)
# cur_series.attachAxis(time_axis_x)
# vol_series.attachAxis(time_axis_x)

# #Create Y1 axis
# cur_axis_y = QValueAxis()
# cur_axis_y.setTitleText("Current[A]")
# cur_axis_y.setLinePenColor(cur_series.pen().color())  #Make the axis and chart colors the same
# cur_axis_y.setRange(0, 5)
# chart.addAxis(cur_axis_y, Qt.AlignLeft)
# cur_series.attachAxis(cur_axis_y)

# #Create Y2 axis
# vol_axis_y = QValueAxis()
# vol_axis_y.setTitleText("Voltage[V]")
# vol_axis_y.setLinePenColor(vol_series.pen().color())  #Make the axis and chart colors the same
# vol_axis_y.setRange(0, 20)
# chart.addAxis(vol_axis_y, Qt.AlignRight)
# vol_series.attachAxis(vol_axis_y)

# cur_vol_chart_view = QChartView()
# cur_vol_chart_view.setChart(chart)
# cur_vol_chart_view.setRenderHint(QPainter.Antialiasing)  #To display the chart smoothly
# cur_vol_chart_view.show()



# for i in range(50000):
#     print(i)
#     cur_vol_chart_view.update()   
# sys.exit(app.exec_())