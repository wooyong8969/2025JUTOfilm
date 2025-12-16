# windows/photo_select.py
'''
PhotoSelectWindow_4, GoodbyeWindow
'''

import os
import cv2
import secrets
import numpy as np

from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMessageBox

from PIL import Image, ImageWin, ImageOps
import win32print
import win32ui

from windows.base import BaseWindow
from windows.qr_window import QRWindow
from utils.qr import make_qr
from state import state
from utils.frame_config import PHOTO_ASPECT


class PhotoSelectWindow_4(BaseWindow):
    """
    6장 중 4장을 선택해서 최종 4컷 결과물을 만드는 화면
    """

    def __init__(self):
        super().__init__()
        uic.loadUi("./page_ui_2025/photo_select_4.ui", self)

        # =========================
        # 디렉토리 준비
        # =========================
        self.photo_dir = state.session1_dir
        self.photos = sorted(os.listdir(self.photo_dir))

        img_dir = state.session2_dir
        os.makedirs(img_dir, exist_ok=True)

        # =========================
        # Session1 → Session2 (CUT)
        # =========================
        for i in range(6, 0, -1):
            if len(self.photos) < i:
                continue

            src_path = os.path.join(self.photo_dir, self.photos[-i])
            cut_img = cv2.imread(src_path)

            existing = sorted(os.listdir(img_dir))
            num = int(existing[-1][-8:-4]) + 1 if existing else 1
            name = f"CUT_{num:05d}.jpg"
            cv2.imwrite(os.path.join(img_dir, name), cut_img)

        self.cut_files = sorted(os.listdir(img_dir))[-6:]
        self.cut_files = [os.path.join(img_dir, f) for f in self.cut_files]

        # =========================
        # UI 썸네일
        # =========================
        self.photo.setPixmap(QPixmap('./pages_img_2025/white.png'))
        self.photo_1.setPixmap(QPixmap(self.cut_files[0]).scaled(QSize(340, 255)))
        self.photo_2.setPixmap(QPixmap(self.cut_files[1]).scaled(QSize(340, 255)))
        self.photo_3.setPixmap(QPixmap(self.cut_files[2]).scaled(QSize(340, 255)))
        self.photo_4.setPixmap(QPixmap(self.cut_files[3]).scaled(QSize(340, 255)))
        self.photo_5.setPixmap(QPixmap(self.cut_files[4]).scaled(QSize(340, 255)))
        self.photo_6.setPixmap(QPixmap(self.cut_files[5]).scaled(QSize(340, 255)))

        # =========================
        # 선택 상태
        # =========================
        state.selected = [0, 0, 0, 0]
        self.button_slots = [-1] * 6
        self.result_image = None

        # =========================
        # 버튼 연결
        # =========================
        self.photo_choice_1.clicked.connect(lambda: self._toggle_select(0, self.photo_1))
        self.photo_choice_2.clicked.connect(lambda: self._toggle_select(1, self.photo_2))
        self.photo_choice_3.clicked.connect(lambda: self._toggle_select(2, self.photo_3))
        self.photo_choice_4.clicked.connect(lambda: self._toggle_select(3, self.photo_4))
        self.photo_choice_5.clicked.connect(lambda: self._toggle_select(4, self.photo_5))
        self.photo_choice_6.clicked.connect(lambda: self._toggle_select(5, self.photo_6))

        self.move_next.clicked.connect(self._on_next)

        self._update_preview()

    # =====================================================
    # 이미지 처리
    # =====================================================

    def _merge_4cut(self, frame_path, f1, f2, f3, f4):
        def safe(p):
            return p if p else './pages_img_2025/white.png'

        # 프레임(RGBA) 읽기
        frame_rgba = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)  # (H,W,4)
        fh, fw = frame_rgba.shape[:2]

        # 배경 캔버스(프레임 크기와 동일하게)
        main_image = cv2.imread('./pages_img_2025/white.png')
        if main_image is None or main_image.shape[:2] != (fh, fw):
            main_image = np.full((fh, fw, 3), 255, dtype=np.uint8)

        alpha = frame_rgba[:, :, 3]

        # 프레임에서 "사진이 보여야 하는 창" 찾기: 보통 창 부분이 투명(alpha==0)입니다.
        win = (alpha == 0).astype(np.uint8) * 255

        contours, _ = cv2.findContours(win, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        rects = [cv2.boundingRect(c) for c in contours]  # (x,y,w,h)

        # 큰 4개만 사용
        rects = sorted(rects, key=lambda r: r[2]*r[3], reverse=True)[:4]

        # 위/아래 행으로 정렬해서 [좌상, 우상, 좌하, 우하] 순서로 맞춤
        rects = sorted(rects, key=lambda r: (r[1], r[0]))
        top = sorted(rects[:2], key=lambda r: r[0])
        bot = sorted(rects[2:], key=lambda r: r[0])
        rects = top + bot

        # 사진 4장 붙이기(창 크기에 맞춤)
        for p, (x, y, w, h) in zip((f1, f2, f3, f4), rects):
            img = cv2.imread(safe(p))
            img = cv2.resize(img, (w, h))
            main_image[y:y+h, x:x+w] = img

        # 프레임 덮기(알파가 있는 부분만)
        frame_bgr = frame_rgba[:, :, :3]
        cv2.copyTo(frame_bgr, alpha, main_image)

        return main_image


    def _update_preview(self):
        res = self._merge_4cut(state.frame_path, *state.selected)
        self.result_image = res
        #res = cv2.rotate(res, cv2.ROTATE_90_CLOCKWISE)
        rgb = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, (910, 615))
        h, w, c = rgb.shape

        qimg = QImage(rgb.data, w, h, w * c, QImage.Format_RGB888)
        self.photo.setPixmap(QPixmap.fromImage(qimg))

    def _toggle_select(self, idx, widget):
        if self.button_slots[idx] == -1:
            try:
                slot = state.selected.index(0)
            except ValueError:
                return
            self.button_slots[idx] = slot
            state.selected[slot] = self.cut_files[idx]
            widget.setStyleSheet("border: 4px solid #DA5451;")
        else:
            slot = self.button_slots[idx]
            state.selected[slot] = 0
            self.button_slots[idx] = -1
            widget.setStyleSheet("border: 0px;")

        self._update_preview()

    # =====================================================
    # 다음 단계 (저장 + QR)
    # =====================================================

    def _on_next(self):
        if not all(state.selected):
            QMessageBox.about(self, '주토필름', '사진 4장을 모두 선택해주세요')
            return

        os.makedirs(state.shared_dir, exist_ok=True)

        # 암호화된 사진 ID
        photo_id = secrets.token_hex(16)

        photo_filename = f"{photo_id}.jpg"
        photo_path = os.path.join(state.shared_dir, photo_filename)

        cv2.imwrite(photo_path, self.result_image)

        download_url = f"http://{state.server_ip}:5000/photos/{photo_filename}"

        qr_path = make_qr(
            download_url=download_url,
            save_dir=state.shared_dir,
            photo_id=photo_id
        )

        self.w = QRWindow(qr_path, photo_path)
        self.w.showFullScreen()
        self.close()


class GoodbyeWindow(BaseWindow):
    """
    결과 출력 및 마지막 화면
    """

    def __init__(self):
        super().__init__()
        uic.loadUi("./page_ui_2025/goodbye.ui", self)

        # Session1에 흑색 이미지 하나 추가
        photo_dir = state.session1_dir
        photos = sorted(os.listdir(photo_dir))

        try:
            num = int(photos[-1][-8:-4]) + 1 if photos else 1
        except ValueError:
            num = 1

        name = f"DSC_{num:05d}.jpg"
        temp = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.imwrite(os.path.join(photo_dir, name), temp)

        # 결과 이미지 출력
        self.img_dir = state.result_dir
        imgs = sorted(os.listdir(self.img_dir))
        self.img_path = os.path.join(self.img_dir, imgs[-1])

        self._print_image(self.img_path)

        from PyQt5.QtCore import QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._go_main)
        self.timer.start(5000)

    def _print_image(self, file_path: str):
        try:
            img = Image.open(file_path)
            img = img.rotate(90, expand=True)

            rotated = ImageOps.expand(img, border=(40, 38, 0, 0), fill='white')

            printer = win32print.OpenPrinter(state.printer_name)
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(state.printer_name)

            for _ in range(state.print_num):
                hdc.StartDoc('Print Job')
                hdc.StartPage()
                dib = ImageWin.Dib(rotated)
                dib.draw(hdc.GetHandleOutput(), (0, 0, *rotated.size))
                hdc.EndPage()
                hdc.EndDoc()

            hdc.DeleteDC()
            win32print.ClosePrinter(printer)

        except Exception as e:
            print("PRINT ERROR:", e)

    def _go_main(self):
        self.timer.stop()
        from windows.start_flow import MainWindow
        self.goto(MainWindow)
