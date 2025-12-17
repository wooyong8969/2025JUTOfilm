import cv2
import numpy as np

def merge_4cut(frame_path, f1, f2, f3, f4, white_path="./pages_img_2025/white.png"):
    def safe(p):
        return p if p else white_path

    # 프레임 RGBA 로드
    frame_rgba = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)
    if frame_rgba is None or frame_rgba.shape[2] != 4:
        raise ValueError("프레임 PNG는 RGBA여야 합니다")

    fh, fw = frame_rgba.shape[:2]

    # 배경 (흰색)
    main_image = np.full((fh, fw, 3), 255, dtype=np.uint8)

    alpha = frame_rgba[:, :, 3].astype(np.float32) / 255.0

    mask = (alpha < 0.01).astype(np.uint8) * 255
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rects = [cv2.boundingRect(c) for c in contours]
    rects = sorted(rects, key=lambda r: r[2]*r[3], reverse=True)[:4]

    rects = sorted(rects, key=lambda r: (r[1], r[0]))
    top = sorted(rects[:2], key=lambda r: r[0])
    bot = sorted(rects[2:], key=lambda r: r[0])
    rects = top + bot

    for p, (x, y, w, h) in zip((f1, f2, f3, f4), rects):
        img = cv2.imread(safe(p), cv2.IMREAD_COLOR)
        img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
        main_image[y:y+h, x:x+w] = img

    frame_rgb = frame_rgba[:, :, :3].astype(np.float32)

    alpha_3 = np.dstack([alpha, alpha, alpha])
    main_f = main_image.astype(np.float32)

    out = frame_rgb * alpha_3 + main_f * (1.0 - alpha_3)

    return out.astype(np.uint8)
