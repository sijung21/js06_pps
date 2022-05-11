
import datetime
import sys
import os
import time
import math
from typing_extensions import Self
import vlc

import cv2
import numpy as np
import pandas as pd
from multiprocessing import Process, Queue
import multiprocessing as mp

# print(PyQt5.__version__)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QBrush, QColor, QPen, QImage, QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QVBoxLayout, QWidget, QLabel, QInputDialog, QGraphicsScene, QGraphicsView, QFrame, QTabWidget
from PyQt5.QtCore import QPoint, QRect, Qt, QRectF, QSize, QCoreApplication, pyqtSlot, QTimer, QUrl
from PyQt5 import uic
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem

from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtWebEngineCore
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis


class GraFanaMainWindow(QWidget):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "ui/grafana.ui")
        uic.loadUi(ui_path, self)
        
        self.webview = QtWebEngineWidgets.QWebEngineView()
        self.webview.setUrl(QUrl("http://localhost:3000/d/6N2W3rQnkw/js06_visibility_dashboard?orgId=1&from=now-3h&to=now&kiosk"))
        self.webview.setZoomFactor(1)
        self.webview.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.webview.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.webview.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.web_verticalLayout.addWidget(self.webview)