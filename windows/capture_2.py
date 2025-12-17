# windows/capture.py
'''
CaptureWindow
'''

import threading
import time
import os

import cv2
import qimage2ndarray

from PyQt5 import uic
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from windows.base_0 import BaseWindow
from state import state
from utils.frame_config import PHOTO_ASPECT


class CaptureWindow(BaseWindow):
    """
    OBS Virtual Camera 기반 촬영 화면 (4컷 전용)
    """
    def __init__(self):
        super().__init__()
        uic.loadUi("./page_ui_2025/capture.ui", self)

        # ===== UI =====
        self.label.setAlignment(Qt.AlignCenter)

        # ===== Camera (OBS Virtual Camera index) =====
        self.cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("카메라(OBS Virtual Camera)를 열 수 없습니다.")

        self.running = True

        # ===== Capture config =====
        self.timelimit = state.timelimit
        self.numlimit = state.numlimit

        self.count = self.timelimit + 1
        self.num = 1

        self.last_frame = None      # crop 완료된 저장용 프레임
        self.preview_qimage = None  # UI 표시용

        # ===== Shutter sound (MP3) =====
        self._init_shutter_sound()

        # ===== Preview thread =====
        self.thread = threading.Thread(
            target=self._run_preview,
            daemon=True
        )
        self.thread.start()

        # ===== Countdown timer =====
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

        # ===== UI refresh timer =====
        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self._update_preview_ui)
        self.preview_timer.start(30)

        self.force_capture = False


    # ==================================================
    # MP3 shutter init / play
    # ==================================================
    def _init_shutter_sound(self):
        # capture.py와 같은 폴더에 shutter.mp3가 있다고 가정함
        self.shutter_path = os.path.join(os.path.dirname(__file__), "shutter.mp3")

        self.shutter_player = QMediaPlayer(self)
        if os.path.exists(self.shutter_path):
            url = QUrl.fromLocalFile(os.path.abspath(self.shutter_path))
            self.shutter_player.setMedia(QMediaContent(url))
            self.shutter_player.setVolume(100)
        else:
            # 파일이 없으면 조용히 넘어가되, 재생 시도는 하지 않도록 함
            self.shutter_path = None

    def _play_shutter(self):
        if not self.shutter_path:
            return
        # 연속 촬영에서도 항상 처음부터 재생되도록 stop + position 0 처리
        self.shutter_player.stop()
        self.shutter_player.setPosition(0)
        self.shutter_player.play()


    # ==================================================
    # 4컷 비율 crop (절대 resize 이전)
    # ==================================================
    def _crop_for_4cut(self, img):
        """
        img: 원본 비율이 유지된 프레임
        return: PHOTO_ASPECT 기준으로 중앙 crop된 프레임
        """
        target_ratio = PHOTO_ASPECT
        h, w, _ = img.shape
        cur_ratio = w / h

        if cur_ratio > target_ratio:
            # 가로가 더 긴 경우 → 좌우 crop
            new_w = int(h * target_ratio)
            x = (w - new_w) // 2
            img = img[:, x:x + new_w]
        else:
            # 세로가 더 긴 경우 → 상하 crop
            new_h = int(w / target_ratio)
            y = (h - new_h) // 2
            img = img[y:y + new_h, :]

        return img


    # ==================================================
    # Camera preview thread
    # ==================================================
    def _run_preview(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.resize(frame, (1920, 1080))

            # 좌우 반전 (OBS에서 안 했다면 여기서)
            frame = cv2.flip(frame, 1)

            # 비율 기준 crop (resize 금지)
            cropped = self._crop_for_4cut(frame)

            # 저장용 (crop 결과 그대로)
            self.last_frame = cropped.copy()

            # UI 미리보기용 변환
            preview = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
            self.preview_qimage = qimage2ndarray.array2qimage(
                preview,
                normalize=False
            )

            time.sleep(0.03)


    # ==================================================
    # UI preview update (메인 스레드)
    # ==================================================
    def _update_preview_ui(self):
        if not self.running or self.preview_qimage is None:
            return

        pixmap = QPixmap.fromImage(self.preview_qimage).scaled(
            self.label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.label.setPixmap(pixmap)


    # ==================================================
    # Countdown tick
    # ==================================================
    def _tick(self):
        if self.count > 1:
            self.count -= 1
            self.count_label.setPixmap(
                QPixmap(f'./count/{self.count}.png')
            )

            if self.num == 1 and self.count == self.timelimit:
                self.count_label_2.setPixmap(QPixmap('./count/1.png'))

        else:
            # 촬영 시점
            self.count_label.clear()
            self.count = self.timelimit + 1
            self.num += 1

            self._capture_one()

            if self.num <= self.numlimit:
                self.count_label_2.setPixmap(
                    QPixmap(f'./count/{self.num}.png')
                )
            else:
                self._finish_capture()


    # ==================================================
    # Save one photo (crop 결과 그대로)
    # ==================================================
    def _capture_one(self):
        if self.last_frame is None:
            return

        # 셔터 사운드 먼저 재생
        self._play_shutter()

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


    # ==================================================
    # Finish capture
    # ==================================================
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


    # ==================================================
    # Next window
    # ==================================================
    def _go_next(self):
        from windows.photo_select_3 import PhotoSelectWindow_4
        self.goto(PhotoSelectWindow_4)


    # ==================================================
    # Key events
    # ==================================================
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
