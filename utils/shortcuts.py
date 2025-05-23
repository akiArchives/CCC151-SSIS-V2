from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt

def add_shortcuts(window):
    shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), window)
    shortcut.activated.connect(lambda: unselect_all_rows(window))

def unselect_all_rows(window):
    if hasattr(window, "students_table"):
        window.students_table.clearSelection()
    if hasattr(window, "programs_table"):
        window.programs_table.clearSelection()
    if hasattr(window, "colleges_table"):
        window.colleges_table.clearSelection()