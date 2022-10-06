import sys

from PyQt5.QtWidgets import QWidget, QApplication, QLabel
from PyQt5.QtCore import Qt, QSize, QPoint, QPointF, QRectF,QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup,pyqtSlot, pyqtProperty, QParallelAnimationGroup
from PyQt5.QtGui import QColor, QBrush, QPaintEvent, QPen, QPainter

class Weather_Icon(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.resize(600, 600)
        # self.child = QLabel(self)
        # self.child.setStyleSheet("background-color:black;border-radius:50px;")
        # self.child.resize(100, 100)
        # self.anim = QPropertyAnimation(self.child, b"pos")
        # self.anim.setEndValue(QPoint(200, 200))
        # self.anim.setDuration(1)
        # self.anim2 = QPropertyAnimation(self.child, b"size")        
        # self.anim2.setEndValue(QSize(300, 200))
        # self.anim2.setDuration(1500)
        # self.anim2.setLoopCount(4)
        # self.anim.start()
        # self.child2 = QWidget(self)
        # self.child2.setStyleSheet("background-color:black;border-radius:50px;")
        # self.child2.resize(100, 100)
        # self.anim2 = QPropertyAnimation(self.child, b"size")
        # self.anim2.setStartValue(QPoint(250, 200))
        # self.anim2.setEndValue(QSize(300, 300))
        # self.anim2.setDuration(1500)
        print("이거 실행중입니다")
        self._cloud_radius = 0
        # self.circle = QLabel(self)
        # self.circle.setStyleSheet("background-color:black;border-radius:50px;")
        # self.circle.resize(100, 100)
        self.anim = QPropertyAnimation(self, b"cloud_radius", self)
        self.anim.setStartValue(20)
        self.anim.setEndValue(25)
        self.anim.setDuration(1500)
        # self.anim.setLoopCount(1000)
        # self.anim.start()
        
        self.anim2 = QPropertyAnimation(self, b"cloud_radius", self)
        self.anim2.setStartValue(25)
        self.anim2.setEndValue(20)
        self.anim2.setDuration(1500)
        
        self.anim_group = QSequentialAnimationGroup()
        self.anim_group.addAnimation(self.anim)
        self.anim_group.addAnimation(self.anim2)
        self.anim_group.setLoopCount(1000)
        
        self.anim_group.start()
        
        # self.anim.start()
        # self.child2 = QWidget(self)
        # self.child2.setStyleSheet("background-color:blue;border-radius:15px;")
        # self.child2.resize(100, 100)        
        # self.anim2 = QPropertyAnimation(self.child2, b"pos")
        # self.anim2.setStartValue(QPoint(200, 0))
        # self.anim2.setEndValue(QPoint(500, 200))
        # self.anim2.setDuration(1500)
        # self.anim2.start()
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cloud_color = QColor(180, 180, 250)
        br = QBrush(cloud_color)
        p.setBrush(br)
        p.setPen(QPen(cloud_color, 2, Qt.SolidLine))
        p.drawEllipse(QPointF(30,50), self._cloud_radius , self._cloud_radius)
        p.drawEllipse(QPointF(50,50), self._cloud_radius , self._cloud_radius)
        p.drawEllipse(QPointF(70,50), self._small_cloud_radius , self._small_cloud_radius)
        p.drawEllipse(QPointF(45,40), self._cloud_radius , self._cloud_radius)     
        # p.drawEllipse(QPointF(55,40), self._cloud_radius , self._cloud_radius)

    
    @pyqtProperty(float)
    def cloud_radius(self):
        return self._cloud_radius
    
    
    @cloud_radius.setter
    def cloud_radius(self, pos):
        self._cloud_radius = pos
        self._small_cloud_radius = pos - 2
        self.update()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Weather_Icon()
    window.show()
    sys.exit(app.exec_())
