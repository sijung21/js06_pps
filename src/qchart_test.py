import random
import sys

from PyQt5.QtChart import (QChart,
                           QChartView,
                           QLineSeries,
                           QValueAxis,
                           QDateTimeAxis)
from PyQt5.QtCore import (QDateTime,
                          Qt)
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication

def keyPressEvent(e):
    """Override function QMainwindow KeyPressEvent that works when key is pressed"""
    if e.key() == Qt.Key_Escape:
        sys.exit()
        
app = QApplication(sys.argv)
cur_series = QLineSeries()
vol_series = QLineSeries()
now = QDateTime.currentDateTime()

#Create appropriate data
for i in range(100, 1, -1):
    cur = 5 * random.random()
    vol = 20 * random.random()
    time = now.addSecs(-i).toMSecsSinceEpoch()  #Processing to append to QLineSeries
    cur_series.append(time, cur)
    vol_series.append(time, vol)

chart = QChart()
chart.setAnimationOptions(QChart.SeriesAnimations)
chart.legend().hide()
chart.addSeries(cur_series)
chart.addSeries(vol_series)

#Create X axis
time_axis_x = QDateTimeAxis()
time_axis_x.setFormat("hh:mm:ss")
chart.addAxis(time_axis_x, Qt.AlignBottom)
cur_series.attachAxis(time_axis_x)
vol_series.attachAxis(time_axis_x)

#Create Y1 axis
cur_axis_y = QValueAxis()
cur_axis_y.setTitleText("Current[A]")
cur_axis_y.setLinePenColor(cur_series.pen().color())  #Make the axis and chart colors the same
cur_axis_y.setRange(0, 5)
chart.addAxis(cur_axis_y, Qt.AlignLeft)
cur_series.attachAxis(cur_axis_y)

#Create Y2 axis
vol_axis_y = QValueAxis()
vol_axis_y.setTitleText("Voltage[V]")
vol_axis_y.setLinePenColor(vol_series.pen().color())  #Make the axis and chart colors the same
vol_axis_y.setRange(0, 20)
chart.addAxis(vol_axis_y, Qt.AlignRight)
vol_series.attachAxis(vol_axis_y)

cur_vol_chart_view = QChartView()
cur_vol_chart_view.setChart(chart)
cur_vol_chart_view.setRenderHint(QPainter.Antialiasing)  #To display the chart smoothly
cur_vol_chart_view.show()

cur_vol_chart_view.update()
        
sys.exit(app.exec_())