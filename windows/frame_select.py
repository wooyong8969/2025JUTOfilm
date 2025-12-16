# windows/frame_select.py
'''
FrameSelectWindow_4
'''

from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox

from windows.base import BaseWindow
from state import state


class FrameSelectWindow_4(BaseWindow):
    """
    4컷 프레임 선택 화면
    """
    def __init__(self):
        super().__init__()
        uic.loadUi("./page_ui_2025/frame_select_4.ui", self)

        state.frame_path = None
        state.frame_index = None

        self.move_previous.clicked.connect(self.on_prev)
        self.move_next.clicked.connect(self.on_next)

        self.frame_choice_1.clicked.connect(lambda: self.select_frame(1))
        self.frame_choice_2.clicked.connect(lambda: self.select_frame(2))
        self.frame_choice_3.clicked.connect(lambda: self.select_frame(3))
        self.frame_choice_4.clicked.connect(lambda: self.select_frame(4))
        self.frame_choice_5.clicked.connect(lambda: self.select_frame(5))
        self.frame_choice_6.clicked.connect(lambda: self.select_frame(6))
        self.frame_choice_7.clicked.connect(lambda: self.select_frame(7))
        self.frame_choice_8.clicked.connect(lambda: self.select_frame(8))
        self.frame_choice_9.clicked.connect(lambda: self.select_frame(9))
        self.frame_choice_10.clicked.connect(lambda: self.select_frame(10))
        self.frame_choice_11.clicked.connect(lambda: self.select_frame(11))
        self.frame_choice_12.clicked.connect(lambda: self.select_frame(12))

    def select_frame(self, n: int):
        """
        프레임 번호 n 선택
        """
        self._update_border(n)
        state.frame_path = f'./frame_2025/{n}.png'
        state.frame_index = n

    def _update_border(self, n: int):
        """
        선택된 프레임에 체크 표시
        """
        frames = [self.frame_1, self.frame_2, self.frame_3, self.frame_4, self.frame_5, self.frame_6, self.frame_7, self.frame_8, self.frame_9, self.frame_10, self.frame_11, self.frame_12]
        for f in frames:
            f.setPixmap(QPixmap())

        target = frames[n - 1]
        target.setPixmap(QPixmap('./pages_img_2025/print_num/check.png'))
        target.setScaledContents(True)

    def on_prev(self):
        from windows.start_flow import NumSelectWindow
        self.goto(NumSelectWindow)

    def on_next(self):
        if state.frame_path:
            from windows.capture import CaptureWindow
            self.goto(CaptureWindow)
        else:
            QMessageBox.about(self, '주토필름', '프레임을 선택해주세요')
