from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import uic

from utils.printer import print_image
from state import state


class QRWindow(QMainWindow):
    def __init__(self, qr_path, result_path):
        super().__init__()
        uic.loadUi("./page_ui_2025/qr.ui", self)
    
        self.result_path = result_path

        self.qr_label.setPixmap(
            QPixmap(qr_path).scaled(
                self.qr_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        self.print_button.clicked.connect(self._print)
        self.exit_button.clicked.connect(self._exit)

    def _print(self):
        try:
            print_image(
                image_path=self.result_path,
                printer_name=state.printer_name,
                copies=state.print_num
            )
            QMessageBox.information(self, "출력", "출력이 완료되었습니다.")

        except Exception as e:
            QMessageBox.critical(
                self,
                "출력 오류",
                str(e)
            )

    def _exit(self):
        from windows.start_flow_1 import MainWindow
        self.w = MainWindow()
        self.w.showFullScreen()
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self._exit()
