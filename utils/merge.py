# utils/merge.py
import cv2
import numpy as np

def merge_4cut(frame_path, f1, f2, f3, f4, white_path="./pages_img_2025/white.png"):
    def safe(p):
        return p if p else white_path

    frame_rgba = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)
    fh, fw = frame_rgba.shape[:2]

    main_image = cv2.imread(white_path)
    if main_image is None or main_image.shape[:2] != (fh, fw):
        main_image = np.full((fh, fw, 3), 255, dtype=np.uint8)

    alpha = frame_rgba[:, :, 3]
    win = (alpha == 0).astype(np.uint8) * 255

    contours, _ = cv2.findContours(win, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = [cv2.boundingRect(c) for c in contours]
    rects = sorted(rects, key=lambda r: r[2]*r[3], reverse=True)[:4]

    rects = sorted(rects, key=lambda r: (r[1], r[0]))
    top = sorted(rects[:2], key=lambda r: r[0])
    bot = sorted(rects[2:], key=lambda r: r[0])
    rects = top + bot

    for p, (x, y, w, h) in zip((f1, f2, f3, f4), rects):
        img = cv2.imread(safe(p))
        img = cv2.resize(img, (w, h))
        main_image[y:y+h, x:x+w] = img

    frame_bgr = frame_rgba[:, :, :3]
    cv2.copyTo(frame_bgr, alpha, main_image)
    return main_image
