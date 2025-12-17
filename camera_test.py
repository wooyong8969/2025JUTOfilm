import cv2

CAM_INDEX = 2  # ← 여기만 바꿔서 테스트

cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ Camera open failed")
    exit()

print("✅ Camera opened")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Frame read failed")
        break
    ret, frame = cap.read()
    print(frame.shape)

    frame = cv2.resize(frame, (1920, 1080))

    cv2.imshow("OBS Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
