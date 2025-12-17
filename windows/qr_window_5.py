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
        self._printed = False  # 출력 1회 제한 플래그

        self.qr_label.setPixmap(
            QPixmap(qr_path).scaled(
                self.qr_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        self.print_button.clicked.connect(self._print_once)
        self.exit_button.clicked.connect(self._exit)

    def _print_once(self):
        # 이미 한 번 출력했으면 무시
        if self._printed:
            return

        self._printed = True
        self.print_button.setEnabled(False)  # 출력 버튼만 막음

        try:
            print_image(
                image_path=self.result_path,
                printer_name=state.printer_name,
                copies=state.print_num
            )
            QMessageBox.information(self, "출력", "출력이 완료되었습니다.")
        except Exception as e:
            # 실패했을 때 다시 출력 가능하게 할지 여부는 선택 사항임
            # "실패해도 1회만"이면 아래 두 줄을 삭제하면 됨
            self._printed = False
            self.print_button.setEnabled(True)

            QMessageBox.critical(self, "출력 오류", str(e))

    def _exit(self):
        from windows.start_flow_1 import MainWindow
        self.w = MainWindow()
        self.w.showFullScreen()
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self._exit()
