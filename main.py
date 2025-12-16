# main.py

import sys
from PyQt5.QtWidgets import QApplication
from windows import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.showFullScreen()
    sys.exit(app.exec_())
