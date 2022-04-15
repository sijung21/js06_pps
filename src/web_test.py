# -------------------------------------------------------------------------------------------------------------------- #
# File Name    : WebPageWidget.py
# Project Name : WebBrowser
# Author       : Yogyui
# Description  : Implementation of basic web page (viewer) widget
# -------------------------------------------------------------------------------------------------------------------- #
import os
from PyQt5.QtCore import Qt, QUrl, QSize, QObject, QEvent
from PyQt5.QtGui import QIcon, QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineHistory


class WebView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QApplication.instance().installEventFilter(self)

    def load(self, *args):
        if isinstance(args[0], QUrl):
            qurl: QUrl = args[0]
            if qurl.isRelative():
                qurl.setScheme('http')
            return super().load(qurl)
        return super().load(*args)

    def release(self):
        self.deleteLater()
        self.close()

    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        if a0.parent() == self:
            if a1.type() == QEvent.MouseButtonPress:
                if a1.button() == Qt.ForwardButton:
                    self.forward()
                elif a1.button() == Qt.BackButton:
                    self.back()
            elif a1.type() == QEvent.Wheel:
                modifier = QApplication.keyboardModifiers()
                if modifier == Qt.ControlModifier:
                    y_angle = a1.angleDelta().y()
                    factor = self.zoomFactor()
                    if y_angle > 0:
                        self.setZoomFactor(factor + 0.1)
                        return True
                    elif y_angle < 0:
                        self.setZoomFactor(factor - 0.1)
                        return True
        return False


class WebPageWidget(QWidget):
    _is_loading: bool = False

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        path_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.getcwd() != path_:
            os.chdir(path_)
        self._editUrl = QLineEdit()
        self._btnGoBackward = QPushButton()
        self._btnGoForward = QPushButton()
        self._btnStopRefresh = QPushButton()
        self._iconRefresh = QIcon('./Resource/reload.png')
        self._iconStop = QIcon('./Resource/cancel.png')
        self._btnZoomIn = QPushButton()
        self._btnZoomOut = QPushButton()
        self._webview = WebView()
        self.initControl()
        self.initLayout()
        self.load('about:blank')

    def release(self):
        self._webview.release()

    def initLayout(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 4, 0, 0)
        vbox.setSpacing(4)

        subwgt = QWidget()
        subwgt.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        hbox = QHBoxLayout(subwgt)
        hbox.setContentsMargins(4, 0, 4, 0)
        hbox.setSpacing(4)
        hbox.addWidget(self._btnGoBackward)
        hbox.addWidget(self._btnGoForward)
        hbox.addWidget(self._btnStopRefresh)
        hbox.addWidget(self._editUrl)
        hbox.addWidget(self._btnZoomIn)
        hbox.addWidget(self._btnZoomOut)
        vbox.addWidget(subwgt)
        vbox.addWidget(self._webview)

    def initControl(self):
        self._editUrl.returnPressed.connect(self.onEditUrlReturnPressed)
        self._webview.loadStarted.connect(self.onWebViewLoadStarted)
        self._webview.loadProgress.connect(self.onWebViewLoadProgress)
        self._webview.loadFinished.connect(self.onWebViewLoadFinished)
        self._btnGoBackward.setEnabled(False)
        self._btnGoBackward.clicked.connect(lambda: self._webview.back())
        self._btnGoBackward.setIcon(QIcon('./Resource/previous.png'))
        self._btnGoBackward.setFlat(True)
        self._btnGoBackward.setIconSize(QSize(20, 20))
        self._btnGoBackward.setFixedSize(QSize(24, 20))
        self._btnGoForward.setEnabled(False)
        self._btnGoForward.clicked.connect(lambda: self._webview.forward())
        self._btnGoForward.setIcon(QIcon('./Resource/forward.png'))
        self._btnGoForward.setFlat(True)
        self._btnGoForward.setIconSize(QSize(20, 20))
        self._btnGoForward.setFixedSize(QSize(24, 20))
        self._btnStopRefresh.setEnabled(False)
        self._btnStopRefresh.clicked.connect(self.onClickBtnStopRefresh)
        self._btnStopRefresh.setIcon(self._iconRefresh)
        self._btnStopRefresh.setFlat(True)
        self._btnStopRefresh.setIconSize(QSize(20, 20))
        self._btnStopRefresh.setFixedSize(QSize(24, 20))
        self._btnZoomIn.clicked.connect(self.onClickBtnZoomIn)
        self._btnZoomIn.setIcon(QIcon('./Resource/zoomin.png'))
        self._btnZoomIn.setFlat(True)
        self._btnZoomIn.setIconSize(QSize(20, 20))
        self._btnZoomIn.setFixedSize(QSize(24, 20))
        self._btnZoomOut.clicked.connect(self.onClickBtnZoomOut)
        self._btnZoomOut.setIcon(QIcon('./Resource/zoomout.png'))
        self._btnZoomOut.setFlat(True)
        self._btnZoomOut.setIconSize(QSize(20, 20))
        self._btnZoomOut.setFixedSize(QSize(24, 20))

    def load(self, url: str):
        self._webview.load(QUrl(url))

    def onEditUrlReturnPressed(self):
        url = self._editUrl.text()
        self.load(url)

    def onWebViewLoadStarted(self):
        self._is_loading = True
        self._btnStopRefresh.setEnabled(True)
        self._btnStopRefresh.setIcon(self._iconStop)

    def onWebViewLoadProgress(self, progress: int):
        pass

    def onWebViewLoadFinished(self, result: bool):
        self._is_loading = False
        url: QUrl = self._webview.url()
        self._editUrl.setText(url.toString())
        history: QWebEngineHistory = self._webview.history()
        self._btnGoBackward.setEnabled(history.canGoBack())
        self._btnGoForward.setEnabled(history.canGoForward())
        self._btnStopRefresh.setIcon(self._iconRefresh)

    def onClickBtnStopRefresh(self):
        if self._is_loading:
            self._webview.stop()
        else:
            self._webview.reload()

    def onClickBtnZoomIn(self):
        factor = self._webview.zoomFactor()
        self._webview.setZoomFactor(factor + 0.1)

    def onClickBtnZoomOut(self):
        factor = self._webview.zoomFactor()
        self._webview.setZoomFactor(factor - 0.1)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_F5:
            self._webview.reload()
        elif a0.key() == Qt.Key_Escape:
            self._webview.stop()
        elif a0.key() == Qt.Key_Backspace:
            self._webview.back()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        pass


if __name__ == '__main__':
    import sys
    from PyQt5.QtCore import QCoreApplication

    QApplication.setStyle('fusion')
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    wgt_ = WebPageWidget()
    wgt_.show()
    wgt_.resize(600, 600)

    app.exec_()
    wgt_.release()