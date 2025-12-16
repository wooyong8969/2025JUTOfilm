# windows/base.py

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt


class BaseWindow(QMainWindow):
    """
    공통 기능을 담는 기본 윈도우 클래스
    """

    def goto(self, window_cls, *args):
        self._next_window = window_cls(*args)
        self._next_window.showFullScreen()
        self.close()

    def keyPressEvent(self, event):
        """
        Q 키 누르면 즉시 프로그램 종료
        """
        if event.key() == Qt.Key_Q:
            QApplication.quit()
        else:
            super().keyPressEvent(event)
