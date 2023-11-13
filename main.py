import sys
from PySide6.QtWidgets import QApplication
from gui_logic import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.showMaximized()
    app.exec()