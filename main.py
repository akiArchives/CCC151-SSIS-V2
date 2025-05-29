import sys
from PyQt6.QtWidgets import QApplication
import mysql.connector
from gui import MainWindow, load_font
import pymysql

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    load_font(app)
    with open("utils/style.qss", "r") as f:
        app.setStyleSheet(f.read())
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())