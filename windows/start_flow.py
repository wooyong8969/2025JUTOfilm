# windows/start_flow.py
'''
MainWindow, ExplainWindow, NumSelectWindow
'''


from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox

from windows.base import BaseWindow
from state import state


class MainWindow(BaseWindow):
    """
    시작 화면
    """
    def __init__(self):
        super().__init__()
        uic.loadUi("./page_ui_v4/main.ui", self)
        self.start.clicked.connect(self.on_start)

    def on_start(self):
        self.goto(ExplainWindow)


class ExplainWindow(BaseWindow):
    """
    사용 방법 설명 화면
    """
    def __init__(self):
        super().__init__()
        uic.loadUi("./page_ui_v4/explain.ui", self)

        self.move_next.clicked.connect(self.on_next)
        self.move_previous.clicked.connect(self.on_prev)

    def on_prev(self):
        self.goto(MainWindow)

    def on_next(self):
        self.goto(NumSelectWindow)


class NumSelectWindow(BaseWindow):
    """
    인쇄할 장 수 선택 화면 (1~4장)
    """
    def __init__(self):
        super().__init__()
        uic.loadUi("./page_ui_v4/num_select.ui", self)

        self.max_num = 4
        state.print_num = 1

        self.label_plus.setPixmap(QPixmap('./img/print_num/plus.png'))
        self.label.setPixmap(QPixmap(f'./count/{state.print_num}.png'))

        self.move_previous.clicked.connect(self.on_prev)
        self.move_next.clicked.connect(self.on_next)
        self.plus.clicked.connect(self.on_plus)
        self.minus.clicked.connect(self.on_minus)

    def on_plus(self):
        if state.print_num < self.max_num:
            state.print_num += 1
            self.label.setPixmap(QPixmap(f'./count/{state.print_num}.png'))
            self.label_plus.setPixmap(QPixmap('./img/print_num/plus.png'))
            self.label_minus.setPixmap(QPixmap('./img/print_num/minus.png'))

        if state.print_num == self.max_num:
            self.label_plus.setPixmap(QPixmap())
            self.label_minus.setPixmap(QPixmap('./img/print_num/minus.png'))

    def on_minus(self):
        if state.print_num > 1:
            state.print_num -= 1
            self.label.setPixmap(QPixmap(f'./count/{state.print_num}.png'))
            self.label_plus.setPixmap(QPixmap('./img/print_num/plus.png'))
            self.label_minus.setPixmap(QPixmap('./img/print_num/minus.png'))

        if state.print_num == 1:
            self.label_minus.setPixmap(QPixmap())
            self.label_plus.setPixmap(QPixmap('./img/print_num/plus.png'))

    def on_prev(self):
        self.goto(ExplainWindow)

    def on_next(self):
        # 4컷 프레임 선택 화면으로 이동
        from windows.frame_select import FrameSelectWindow_4
        self.goto(FrameSelectWindow_4)
