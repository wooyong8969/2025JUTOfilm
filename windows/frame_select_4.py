# windows/frame_select.py
'''
FrameSelectWindow_4
'''

import os
import cv2
import secrets

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMessageBox

from windows.base_0 import BaseWindow
from state import state
from windows.qr_window_5 import QRWindow
from utils.qr import make_qr
from utils.merge import merge_4cut


class FrameSelectWindow_4(BaseWindow):
    """
    4컷 프레임 선택 화면
    """
    def __init__(self):
        super().__init__()
        uic.loadUi("./page_ui_2025/frame_select_4.ui", self)

        state.frame_path = None
        state.frame_index = None

        self.result_image = None  # 최종 합성 결과(BGR)

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

        # 초기 미리보기 비우기
        self.photo.setPixmap(QPixmap())

    def select_frame(self, n: int):
        """
        프레임 번호 n 선택
        """
        self._update_border(n)
        state.frame_path = f'./frame_2025/{n:02d}.png'
        state.frame_index = n

        # 프레임 선택 즉시 합성 + 미리보기
        if self._build_result_image():
            self._update_preview()
        else:
            # 사진 선택이 아직 안 됐거나 합성 실패 시 미리보기 초기화
            self.photo.setPixmap(QPixmap())

    def _build_result_image(self) -> bool:
        """
        state.selected(4장) + state.frame_path로 최종 합성 이미지를 생성합니다.
        성공하면 self.result_image가 채워집니다.
        """
        if not state.frame_path:
            self.result_image = None
            return False

        selected = getattr(state, "selected", None)
        if not selected or len(selected) != 4:
            self.result_image = None
            return False

        f1, f2, f3, f4 = selected
        self.result_image = merge_4cut(state.frame_path, f1, f2, f3, f4)
        return self.result_image is not None

    def _update_preview(self):
        """
        frame_select_4.ui의 QLabel(photo)에 최종 합성본 미리보기를 표시합니다.
        """
        if self.result_image is None:
            self.photo.setPixmap(QPixmap())
            return

        rgb = cv2.cvtColor(self.result_image, cv2.COLOR_BGR2RGB)
        h, w, c = rgb.shape
        qimg = QImage(rgb.data, w, h, w * c, QImage.Format_RGB888)

        pix = QPixmap.fromImage(qimg)
        pix = pix.scaled(self.photo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.photo.setPixmap(pix)

    def _update_border(self, n: int):
        """
        선택된 프레임에 체크 표시
        """
        frames = [
            self.frame_1, self.frame_2, self.frame_3, self.frame_4,
            self.frame_5, self.frame_6, self.frame_7, self.frame_8,
            self.frame_9, self.frame_10, self.frame_11, self.frame_12
        ]
        for f in frames:
            f.setPixmap(QPixmap())

        target = frames[n - 1]
        target.setPixmap(QPixmap('./pages_img_2025/print_num/check.png'))
        target.setScaledContents(True)

    def on_prev(self):
        from windows.photo_select_3 import PhotoSelectWindow_4
        self.goto(PhotoSelectWindow_4)

    def on_next(self):
        if not state.frame_path:
            QMessageBox.about(self, '주토필름', '프레임을 선택해주세요')
            return

        # 저장 직전에 최종 합성 보장
        if not self._build_result_image():
            QMessageBox.about(self, '주토필름', '사진 4장 합성에 실패했습니다')
            return

        os.makedirs(state.shared_dir, exist_ok=True)

        photo_id = secrets.token_hex(16)
        photo_filename = f"{photo_id}.jpg"
        photo_path = os.path.join(state.shared_dir, photo_filename)

        ok = cv2.imwrite(photo_path, self.result_image)
        if not ok:
            QMessageBox.about(self, '주토필름', '최종 이미지 저장에 실패했습니다')
            return

        download_url = f"http://{state.server_ip}:5000/photos/{photo_filename}"

        qr_path = make_qr(
            download_url=download_url,
            save_dir=state.shared_dir,
            photo_id=photo_id
        )

        self.w = QRWindow(qr_path, photo_path)
        self.w.showFullScreen()
        self.close()
