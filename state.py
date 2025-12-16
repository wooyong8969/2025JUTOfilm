# state.py


import os
import datetime

class AppState:
    """
    전역 상태를 한 곳에서 관리하는 클래스 (4컷 전용)
    """
    def __init__(self):
        # 프레임 크기: 4컷 고정
        self.size = 4

        # 선택된 프레임 정보
        self.frame_path = None      # './frame_v2/4frame/1.png' 같은 경로
        self.frame_index = None     # 1, 2, 3 ...

        # 인쇄 매수
        self.print_num = 1

        # 사진 선택 (4컷이므로 4장)
        self.selected = [0, 0, 0, 0]

        # 프린터 이름
        self.printer_name = "Canon SELPHY CP1300"

        # 디렉토리 경로
        self.session1_dir = r"C:\digiCamControl\Session1"
        self.session2_dir = r"C:\digiCamControl\Session2"
        self.result_dir   = "./result"

        # 촬영 관련
        self.timelimit = 10     # 한 장 찍기 전 카운트다운 시간
        self.numlimit  = 6      # 총 촬영 장수

        # QR 다운로드용 공유 폴더
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.shared_dir = os.path.join("shared_photos")

        # 서버
        #self.server_ip = "10.138.24.168"      # <수정해야할곳>10.138.25.216
        self.server_ip = "192.168.137.1"      # <수정해야할곳>

state = AppState()
