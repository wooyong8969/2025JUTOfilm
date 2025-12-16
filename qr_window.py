# windows/qr_window.py

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from PyQt5 import uic

class QRWindow(QMainWindow):
    def __init__(self, qr_path):
        super().__init__()
        uic.loadUi("./page_ui_v3/qr.ui", self)

        self.qr_label.setPixmap(
            QPixmap(qr_path).scaled(
                self.qr_label.size(),
                aspectRatioMode=1
            )
        )

        # 10초 후 자동 종료 → 메인으로
        QTimer.singleShot(10000, self.go_home)

    def go_home(self):
        from windows.start_flow import MainWindow
        self.w = MainWindow()
        self.w.showFullScreen()
        self.close()
