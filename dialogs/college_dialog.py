from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QMessageBox
import mysql.connector

class CollegeDialog(QDialog):
    def __init__(self, db, college=None, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(400)
        self.db = db
        self.college = college
        self.setWindowTitle("Add College" if not college else "Edit College")
        self.setModal(True)

        layout = QFormLayout(self)

        # Code
        self.code = QLineEdit()
        self.code.setObjectName("FormLineEdit")
        self.code.setMaxLength(10)
        layout.addRow("Code:", self.code)

        # Name
        self.name = QLineEdit()
        self.name.setObjectName("FormLineEdit")
        layout.addRow("Name:", self.name)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.setObjectName("FormButtonBox")
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if college:
            self.load_college_data()

    def load_college_data(self):
        self.code.setText(self.college['code'])
        self.name.setText(self.college['name'])

    def validate_and_accept(self):
        code = self.code.text().strip()
        name = self.name.text().strip()

        if not code or not name:
            QMessageBox.warning(self, "Validation Error", "All fields are required!")
            return

        self.accept()

    def get_college_data(self):
        return {
            'code': self.code.text().strip(),
            'name': self.name.text().strip()
        }
