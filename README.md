pip install PyQt5 opencv-python numpy qimage2ndarray qrcode[pil] flask pillow pywin32


- cmd에서 ipconfig로 기본 게이트웨이 주소 확인하기
- 해당 ip를 'state.py'의 self.server_ip로 바꾸기
  ("10.138.24.168"의 경우, 학교 CBE_S 와이파이)

<노트북 변경 시 수정해야 할 곳>
- state.py > self.server_ip, self.printer_name
- windows/capture.py > self.cap
- utils/qr.py > SERVER_BASE