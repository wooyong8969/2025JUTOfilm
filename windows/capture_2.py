# windows/capture.py
'''
CaptureWindow
'''

import threading
import time
import os

import cv2
import numpy as np
import qimage2ndarray

from PyQt5 import uic
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap

from windows.base_0 import BaseWindow
from state import state
from utils.frame_config import PHOTO_ASPECT


class CaptureWindow(BaseWindow):
    """
    웹캠 기반 촬영 화면 (4컷 전용)
    """
    def __init__(self):
        super().__init__()
        uic.loadUi("./page_ui_2025/capture.ui", self)

        self.label.setAlignment(Qt.AlignCenter)

        self.cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)  # <수정해야할곳>
        if not self.cap.isOpened():
            raise RuntimeError("웹캠을 열 수 없습니다.")

        self.running = True

        self.timelimit = state.timelimit
        self.numlimit = state.numlimit

        self.count = self.timelimit + 1
        self.num = 1

        self.last_frame = None          # 마지막 웹캠 프레임 저장용
        self.preview_qimage = None      # UI 표시용 프레임

        # 미리보기 스레드
        self.thread = threading.Thread(
            target=self._run_preview,
            daemon=True
        )
        self.thread.start()

        # 카운트다운 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

        # UI 갱신 타이머 (메인 스레드)
        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self._update_preview_ui)
        self.preview_timer.start(30)

        self.force_capture = False      # N키 중복 방지


    # ==============================
    # 4컷 비율 crop (미리보기 + 저장 공통)
    # ==============================
    def _crop_for_4cut(self, img):
        target_ratio = PHOTO_ASPECT
        h, w, _ = img.shape
        cur_ratio = w / h

        if cur_ratio > target_ratio:
            new_w = int(h * target_ratio)
            x = (w - new_w) // 2
            img = img[:, x:x + new_w]
        else:
            new_h = int(w / target_ratio)
            y = (h - new_h) // 2
            img = img[y:y + new_h, :]

        return img


    # ==============================
    # 웹캠 프레임 처리 (서브 스레드)
    # ==============================
    def _run_preview(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            # 좌우 반전
            frame = cv2.flip(frame, 1)

            # 촬영 기준 크롭
            frame = self._crop_for_4cut(frame)

            # 저장용
            self.last_frame = frame.copy()

            # 미리보기용 변환
            preview = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # preview = cv2.resize(preview, (1400, 1050))

            self.preview_qimage = qimage2ndarray.array2qimage(
                preview,
                normalize=False
            )

            time.sleep(0.03)


    # ==============================
    # 웹캠 미리보기 UI 업데이트 (메인 스레드)
    # ==============================
    def _update_preview_ui(self):
        if not self.running:
            return
        if self.preview_qimage is None:
            return

        pixmap = QPixmap.fromImage(self.preview_qimage).scaled(
            self.label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.label.setPixmap(pixmap)


    # ==============================
    # 타이머 tick
    # ==============================
    def _tick(self):
        if self.count > 1:
            self.count -= 1
            self.count_label.setPixmap(
                QPixmap(f'./count/{self.count}.png')
            )

            if self.num == 1 and self.count == self.timelimit:
                self.count_label_2.setPixmap(QPixmap('./count/1.png'))

        else:
            # 촬영 타이밍
            self.count_label.clear()
            self.count = self.timelimit + 1
            self.num += 1

            self._capture_one()

            if self.num <= self.numlimit:
                self.count_label_2.setPixmap(
                    QPixmap(f'./count/{self.num}.png')
                )
            else:
                # 촬영 종료
                self._finish_capture()


    # ==============================
    # 사진 1장 저장
    # ==============================
    def _capture_one(self):
        if self.last_frame is None:
            return

        os.makedirs(state.session1_dir, exist_ok=True)

        existing = sorted(os.listdir(state.session1_dir))
        if existing:
            try:
                num = int(existing[-1][-8:-4]) + 1
            except ValueError:
                num = 1
        else:
            num = 1

        filename = f"WEBCAM_{num:05d}.png"
        path = os.path.join(state.session1_dir, filename)

        cv2.imwrite(path, self.last_frame)


    # ==============================
    # 촬영 종료 처리
    # ==============================
    def _finish_capture(self):
        self.running = False

        self.timer.stop()
        self.preview_timer.stop()

        if self.cap is not None:
            self.cap.release()

        self.preview_qimage = None
        self.label.clear()
        self.count_label_2.clear()

        self.label_2.setPixmap(
            QPixmap('./pages_img_2025/슬라이드7.png').scaled(
                self.label_2.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        QTimer.singleShot(3000, self._go_next)


    # ==============================
    # 다음 화면
    # ==============================
    def _go_next(self):
        from windows.photo_select_3 import PhotoSelectWindow_4
        self.goto(PhotoSelectWindow_4)


    # ==============================
    # 키 입력 처리
    # ==============================
    def keyPressEvent(self, event):
        # N 키 → 즉시 촬영
        if event.key() == Qt.Key_N:
            if not self.force_capture:
                self.force_capture = True
                self.count = 1
                QTimer.singleShot(0, self._reset_force_flag)

        # Q 키 → 전체 종료
        elif event.key() == Qt.Key_Q:
            from PyQt5.QtWidgets import QApplication
            QApplication.quit()


    def _reset_force_flag(self):
        self.force_capture = False