from utils.printer import print_image

TEST_IMAGE = r"result\20251216111316.jpg"
PRINTER_NAME = "Canon SELPHY CP1300"  # 네 프린터 이름

print_image(
    image_path=TEST_IMAGE,
    printer_name=PRINTER_NAME,
    copies=1
)

print("PRINT TEST DONE")
