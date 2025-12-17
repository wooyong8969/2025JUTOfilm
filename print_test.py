from utils.printer import print_image
from PIL import Image

TEST_IMAGE = r"shared_photos\f29a98fcd0c62c74fef591fec1ab1fce.jpg"
PRINTER_NAME = "Canon SELPHY CP1300"

# === 100 x 148 mm @ 300 DPI ===
TARGET_SIZE = (1747, 1180)  # width, height in pixels
RESIZED_IMAGE = r"shared_photos\_resized_test.jpg"

# === 리사이즈 ===
with Image.open(TEST_IMAGE) as img:
    img = img.convert("RGB")
    img_resized = img.resize(TARGET_SIZE, Image.LANCZOS)
    img_resized.save(RESIZED_IMAGE)

# === 프린트 ===
print_image(
    image_path=RESIZED_IMAGE,
    printer_name=PRINTER_NAME,
    copies=1
)

print("PRINT TEST DONE")
