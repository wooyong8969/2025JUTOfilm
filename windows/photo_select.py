# windows/photo_select.py
'''
PhotoSelectWindow_4, GoodbyeWindow
'''


import os
import datetime

import cv2

from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMessageBox

from PIL import Image, ImageWin, ImageOps
import win32print
import win32ui

from windows.base import BaseWindow
from state import state

from utils.qr import upload_photo, make_qr
from windows.qr_window import QRWindow



import os
import cv2
import datetime

from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMessageBox

from windows.base import BaseWindow
from windows.qr_window import QRWindow
from utils.qr import make_qr
from state import state


class PhotoSelectWindow_4(BaseWindow):
    """
    6장 중 4장을 선택해서 최종 4컷 결과물을 만드는 화면
    """

    def __init__(self):
        super().__init__()
        uic.loadUi("./page_ui_v3/photo_select_4.ui", self)

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
            cut_img = self._cut_for_4cut(src_path)

            existing = sorted(os.listdir(img_dir))
            num = int(existing[-1][-8:-4]) + 1 if existing else 1
            name = f"CUT_{num:05d}.jpg"
            cv2.imwrite(os.path.join(img_dir, name), cut_img)

        self.cut_files = sorted(os.listdir(img_dir))[-6:]
        self.cut_files = [os.path.join(img_dir, f) for f in self.cut_files]

        # =========================
        # UI 썸네일
        # =========================
        self.photo.setPixmap(QPixmap('./white.png'))
        self.photo_1.setPixmap(QPixmap(self.cut_files[0]).scaled(QSize(450, 300)))
        self.photo_2.setPixmap(QPixmap(self.cut_files[1]).scaled(QSize(450, 300)))
        self.photo_3.setPixmap(QPixmap(self.cut_files[2]).scaled(QSize(450, 300)))
        self.photo_4.setPixmap(QPixmap(self.cut_files[3]).scaled(QSize(450, 300)))
        self.photo_5.setPixmap(QPixmap(self.cut_files[4]).scaled(QSize(450, 300)))
        self.photo_6.setPixmap(QPixmap(self.cut_files[5]).scaled(QSize(450, 300)))

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

    def _cut_for_4cut(self, file_path):
        image = cv2.imread(file_path)
        image = cv2.resize(image, (2736, 1824), cv2.INTER_CUBIC)

        target_ratio = 45 / 64
        h, w, _ = image.shape
        cur_ratio = w / h

        if cur_ratio > target_ratio:
            new_w = int(h * target_ratio)
            x = (w - new_w) // 2
            return image[:, x:x + new_w]
        else:
            new_h = int(w / target_ratio)
            y = (h - new_h) // 2
            return image[y:y + new_h, :]

    def _merge_4cut(self, frame_path, f1, f2, f3, f4):
        main_image = cv2.imread('./white.png')

        def safe(p): return p if p else './white_5.png'

        imgs = [cv2.resize(self._cut_for_4cut(safe(p)), None, None, 0.415, 0.415)
                for p in (f1, f2, f3, f4)]

        coords = [(47,165),(47,944),(602,165),(602,944)]
        ih, iw, _ = imgs[0].shape

        for img, (x, y) in zip(imgs, coords):
            main_image[y:y+ih, x:x+iw] = img

        frame = cv2.imread(frame_path)
        mask = cv2.bitwise_not(cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)[:,:,3])
        cv2.copyTo(main_image, mask, frame)
        return frame

    def _update_preview(self):
        res = self._merge_4cut(state.frame_path, *state.selected)
        self.result_image = res

        rgb = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, (510, 740))
        h, w, c = rgb.shape

        qimg = QImage(rgb.data, w, h, w*c, QImage.Format_RGB888)
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
            QMessageBox.about(self, '충곽한컷', '사진 4장을 모두 선택해주세요')
            return

        os.makedirs(state.shared_dir, exist_ok=True)

        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        photo_filename = f"photo_{now}.jpg"
        photo_path = os.path.join(state.shared_dir, photo_filename)

        cv2.imwrite(photo_path, self.result_image)

        download_url = f"http://{state.server_ip}:5000/photos/{photo_filename}"

        qr_path = make_qr(
            download_url=download_url,
            save_dir=state.shared_dir,
            photo_id=now
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
        uic.loadUi("./page_ui_v3/goodbye.ui", self)

        # Session1에 흑색 이미지 하나 추가(원래 코드 패턴 유지)
        photo_dir = state.session1_dir
        photos = sorted(os.listdir(photo_dir))

        if photos:
            try:
                num = int(photos[-1][-8:-4]) + 1
            except ValueError:
                num = 1
        else:
            num = 1

        name = (f"DSC_{num:05d}.jpg")
        temp = cv2.imread('./black.jpg')
        cv2.imwrite(os.path.join(photo_dir, name), temp)

        # 결과 이미지 중 최신 파일
        self.img_dir = state.result_dir
        imgs = sorted(os.listdir(self.img_dir))
        self.img = imgs[-1]
        self.img_path = os.path.join(self.img_dir, self.img)

        # 프린트
        self._print_image(self.img_path)

        # 몇 초 후 메인 화면으로 복귀
        from PyQt5.QtCore import QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._go_main)
        self.timer.start(5000)

    def _print_image(self, file_path: str):
        try:
            img = Image.open(file_path)
            img = img.rotate(90, expand=True)

            move_left = 40
            move_up = 38
            rotated = ImageOps.expand(img, border=(move_left, move_up, 0, 0), fill='white')

            printer = win32print.OpenPrinter(state.printer_name)
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(state.printer_name)

            for _ in range(state.print_num):
                hdc.StartDoc('Print Job')
                hdc.StartPage()
                dib = ImageWin.Dib(rotated)
                dib.draw(hdc.GetHandleOutput(), (0, 0, rotated.size[0], rotated.size[1]))
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
