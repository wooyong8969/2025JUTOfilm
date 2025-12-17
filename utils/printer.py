# utils/printer.py

import win32print
import win32ui
from win32con import HORZRES, VERTRES
from PIL import Image, ImageWin


SAFE_MARGIN = 0.05


def print_image(
    image_path: str,
    printer_name: str,
    copies: int = 1,
    rotate: bool = True,
):
    # 1. 이미지 로드
    img = Image.open(image_path).convert("RGB")

    img = img.resize(
        (1748, 1181),
        Image.LANCZOS
    )

    # 2. 프린터가 강제로 landscape라고 가정 → 이미지로 보정
    if not rotate:
        img = img.rotate(-90, expand=True)

    # 3. 프린터 DC 생성
    hprinter = win32print.OpenPrinter(printer_name)
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)

    try:
        # 4. 프린터 인쇄 가능 영역
        pw = hdc.GetDeviceCaps(HORZRES)
        ph = hdc.GetDeviceCaps(VERTRES)

        # 5. SAFE AREA 적용 (프린터가 잘라도 안 잘리게)
        safe_pw = int(pw * (1 - SAFE_MARGIN))
        safe_ph = int(ph * (1 - SAFE_MARGIN))

        iw, ih = img.size

        # 6. 절대 확대 안 함 (contain)
        scale = min(safe_pw / iw, safe_ph / ih)
        dw = int(iw * scale)
        dh = int(ih * scale)

        # 7. 중앙 정렬
        ox = (pw - dw) // 2
        oy = (ph - dh) // 2

        box = (ox, oy, ox + dw, oy + dh)

        # 8. 출력
        for _ in range(copies):
            hdc.StartDoc(image_path)
            hdc.StartPage()

            dib = ImageWin.Dib(img)
            dib.draw(hdc.GetHandleOutput(), box)

            hdc.EndPage()
            hdc.EndDoc()

    finally:
        hdc.DeleteDC()
        win32print.ClosePrinter(hprinter)
