import sys
import mysql.connector
from PyQt6.QtWidgets import QApplication
from gui import MainWindow, load_font

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    load_font(app)
    with open("utils/style.qss", "r") as f:
        app.setStyleSheet(f.read())
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())