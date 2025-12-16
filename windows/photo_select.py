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



class PhotoSelectWindow_4(BaseWindow):
    """
    6장 중 4장을 선택해서 최종 4컷 결과물을 만드는 화면
    """
    def __init__(self):
        super().__init__()
        uic.loadUi("./page_ui_v3/photo_select_4.ui", self)

        self.photo_dir = state.session1_dir
        self.photos = sorted(os.listdir(self.photo_dir))

        img_dir = state.session2_dir
        os.makedirs(img_dir, exist_ok=True)

        # Session1의 마지막 6장을 잘라서 Session2에 CUT_XXXXX 형식으로 저장
        for i in range(6, 0, -1):
            if len(self.photos) < i:
                continue
            src_path = os.path.join(self.photo_dir, self.photos[-i])
            cut_img = self._cut_for_4cut(src_path)

            existing = sorted(os.listdir(img_dir))
            if existing:
                last_name = existing[-1]
                try:
                    num = int(last_name[-8:-4]) + 1
                except ValueError:
                    num = 1
            else:
                num = 1
            name = (f"CUT_{num:05d}.jpg")
            dst_path = os.path.join(img_dir, name)
            cv2.imwrite(dst_path, cut_img)

        self.cut_files = sorted(os.listdir(img_dir))[-6:]  # 최근 6개만 사용
        self.cut_files = [os.path.join(img_dir, f) for f in self.cut_files]

        # 미리보기 썸네일
        self.photo.setPixmap(QPixmap('./white.png'))
        self.photo_1.setPixmap(QPixmap(self.cut_files[0]).scaled(QSize(450, 300)))
        self.photo_2.setPixmap(QPixmap(self.cut_files[1]).scaled(QSize(450, 300)))
        self.photo_3.setPixmap(QPixmap(self.cut_files[2]).scaled(QSize(450, 300)))
        self.photo_4.setPixmap(QPixmap(self.cut_files[3]).scaled(QSize(450, 300)))
        self.photo_5.setPixmap(QPixmap(self.cut_files[4]).scaled(QSize(450, 300)))
        self.photo_6.setPixmap(QPixmap(self.cut_files[5]).scaled(QSize(450, 300)))

        # 선택 상태
        state.selected = [0, 0, 0, 0]  # 4장
        self.button_slots = [-1] * 6   # 각 버튼이 어떤 slot(0~3)에 매핑됐는지

        self.result_image = None

        # 사진 선택 버튼
        self.photo_choice_1.clicked.connect(lambda: self._toggle_select(0, self.photo_1))
        self.photo_choice_2.clicked.connect(lambda: self._toggle_select(1, self.photo_2))
        self.photo_choice_3.clicked.connect(lambda: self._toggle_select(2, self.photo_3))
        self.photo_choice_4.clicked.connect(lambda: self._toggle_select(3, self.photo_4))
        self.photo_choice_5.clicked.connect(lambda: self._toggle_select(4, self.photo_5))
        self.photo_choice_6.clicked.connect(lambda: self._toggle_select(5, self.photo_6))

        self.move_next.clicked.connect(self._on_next)

        # 초기 미리보기
        self._update_preview()

    def _cut_for_4cut(self, file_path: str):
        """
        원본 사진을 4컷 비율(45:64)에 맞춰 중앙 crop
        """
        image = cv2.imread(file_path)
        image = cv2.resize(image, (2736, 1824), cv2.INTER_CUBIC)

        target_ratio = 45 / 64
        h, w, _ = image.shape
        cur_ratio = w / h

        if cur_ratio > target_ratio:
            new_w = int(h * target_ratio)
            start_x = (w - new_w) // 2
            cropped = image[:, start_x:start_x + new_w]
        else:
            new_h = int(w / target_ratio)
            start_y = (h - new_h) // 2
            cropped = image[start_y:start_y + new_h, :]

        return cropped

    def _merge_4cut(self, frame_path, f1, f2, f3, f4):
        """
        4장의 사진과 프레임 PNG를 합성
        """
        main_image = cv2.imread('./white.png', cv2.IMREAD_COLOR)

        def safe_path(p):
            return p if p else './white_5.png'

        f1 = safe_path(f1)
        f2 = safe_path(f2)
        f3 = safe_path(f3)
        f4 = safe_path(f4)

        img1 = self._cut_for_4cut(f1)
        img2 = self._cut_for_4cut(f2)
        img3 = self._cut_for_4cut(f3)
        img4 = self._cut_for_4cut(f4)

        frame = cv2.imread(frame_path, cv2.IMREAD_COLOR)
        mask = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)[:, :, 3]
        mask = cv2.bitwise_not(mask)

        m = 0.415
        img1 = cv2.resize(img1, None, None, m, m, cv2.INTER_CUBIC)
        img2 = cv2.resize(img2, None, None, m, m, cv2.INTER_CUBIC)
        img3 = cv2.resize(img3, None, None, m, m, cv2.INTER_CUBIC)
        img4 = cv2.resize(img4, None, None, m, m, cv2.INTER_CUBIC)

        x1, y1 = 47, 165
        x2, y2 = 47, 944
        x3, y3 = 602, 165
        x4, y4 = 602, 944

        ih, iw, _ = img1.shape
        main_image[y1:y1+ih, x1:x1+iw] = img1
        main_image[y2:y2+ih, x2:x2+iw] = img2
        main_image[y3:y3+ih, x3:x3+iw] = img3
        main_image[y4:y4+ih, x4:x4+iw] = img4

        cv2.copyTo(main_image, mask, frame)
        return frame

    def _update_preview(self):
        """
        선택된 사진 4장으로 미리보기 이미지 업데이트
        """
        frame_path = state.frame_path
        img_1, img_2, img_3, img_4 = state.selected

        res = self._merge_4cut(frame_path, img_1, img_2, img_3, img_4)
        self.result_image = res

        res_rgb = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
        res_rgb = cv2.resize(res_rgb, (510, 740))

        h, w, c = res_rgb.shape
        qImg = QImage(res_rgb.data, w, h, w * c, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)

        self.photo.setPixmap(pixmap)

    def _toggle_select(self, idx: int, widget):
        """
        6개 후보 중 idx번째 사진 선택/해제
        """
        if self.button_slots[idx] == -1:
            # 아직 선택 안 된 버튼 → 선택 시도
            slot = -1
            for i in range(4):
                if state.selected[i] == 0:
                    slot = i
                    break

            if slot == -1:
                # 이미 4장 다 선택됨
                return

            self.button_slots[idx] = slot
            state.selected[slot] = self.cut_files[idx]
            widget.setStyleSheet("border: 4px solid #DA5451;")
        else:
            # 이미 선택된 버튼 → 해제
            slot = self.button_slots[idx]
            state.selected[slot] = 0
            self.button_slots[idx] = -1
            widget.setStyleSheet("border: 0px solid red;")

        self._update_preview()

    def _on_next(self):
        if not all(state.selected):
            QMessageBox.about(self, '충곽한컷', '사진 4장을 모두 선택해주세요')
            return

        # 1. 결과 이미지 저장
        now = datetime.datetime.now()
        now_str = now.strftime('%Y%m%d%H%M%S')
        os.makedirs(state.result_dir, exist_ok=True)
        save_path = os.path.join(state.result_dir, f'{now_str}.jpg')
        cv2.imwrite(save_path, self.result_image)

        try:
            # 2. 서버로 업로드
            download_url = upload_photo(save_path)

            # 3. QR 코드 생성
            qr_path = make_qr(download_url)

        except Exception as e:
            QMessageBox.about(
                self,
                '오류',
                f'사진 업로드 중 오류가 발생했습니다.\n{e}'
            )
            return

        # 4. QR 화면으로 이동
        self.w = QRWindow(qr_path, save_path)
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
