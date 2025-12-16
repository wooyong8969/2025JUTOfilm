# utils/printer.py

import win32print
import win32ui
from PIL import Image, ImageWin, ImageOps


def print_image(
    image_path: str,
    printer_name: str,
    copies: int = 1,
    rotate: bool = True
):
    """
    이미지 파일을 지정한 프린터로 출력
    """

    img = Image.open(image_path)

    # SELPHY 같은 프린터는 회전 필요
    if rotate:
        img = img.rotate(90, expand=True)

    # 여백 조정 (프린터별 튜닝)
    img = ImageOps.expand(
        img,
        border=(40, 38, 0, 0),
        fill="white"
    )

    hprinter = win32print.OpenPrinter(printer_name)
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)

    try:
        for _ in range(copies):
            hdc.StartDoc(image_path)
            hdc.StartPage()

            dib = ImageWin.Dib(img)
            dib.draw(
                hdc.GetHandleOutput(),
                (0, 0, img.size[0], img.size[1])
            )

            hdc.EndPage()
            hdc.EndDoc()

    finally:
        hdc.DeleteDC()
        win32print.ClosePrinter(hprinter)
