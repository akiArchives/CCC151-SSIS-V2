from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QMessageBox
import mysql.connector

class StudentDialog(QDialog):
    def __init__(self, db, student=None, programs=None, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(400)
        self.db = db
        self.student = student
        self.setWindowTitle("Add Student" if not student else "Edit Student")
        self.setModal(True)

        layout = QFormLayout(self)

        # ID Number (format: YYYY-NNNN)
        self.id_number = QLineEdit()
        self.id_number.setObjectName("FormLineEdit")
        self.id_number.setPlaceholderText("YYYY-NNNN")
        layout.addRow("ID Number:", self.id_number)

        # First Name
        self.first_name = QLineEdit()
        self.first_name.setObjectName("FormLineEdit")
        layout.addRow("First Name:", self.first_name)

        # Last Name
        self.last_name = QLineEdit()
        self.last_name.setObjectName("FormLineEdit")
        layout.addRow("Last Name:", self.last_name)

        # Year Level
        self.year_level = QComboBox()
        self.year_level.setObjectName("FormComboBox")
        self.year_level.addItems(["1", "2", "3", "4", "5"])
        layout.addRow("Year Level:", self.year_level)

        # Gender
        self.gender = QComboBox()
        self.gender.setObjectName("FormComboBox")
        self.gender.addItems(["Male", "Female", "Other"])
        layout.addRow("Gender:", self.gender)

        # Program
        self.program_code = QComboBox()
        self.program_code.setObjectName("FormComboBox")
        if programs:
            for program in programs:
                self.program_code.addItem(f"{program['code']} - {program['name']}", program['code'])
        layout.addRow("Program:", self.program_code)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.setObjectName("FormButtonBox")
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if student:
            self.load_student_data()

    def load_student_data(self):
        self.id_number.setText(self.student['id_number'])
        self.first_name.setText(self.student['first_name'])
        self.last_name.setText(self.student['last_name'])
        self.year_level.setCurrentText(str(self.student['year_level']))
        self.gender.setCurrentText(self.student['gender'])
        
        # Find the index of the student's program
        index = self.program_code.findData(self.student['program_code'])
        if index >= 0:
            self.program_code.setCurrentIndex(index)

    def validate_and_accept(self):
        id_number = self.id_number.text().strip()
        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()
        program_code = self.program_code.currentData()

        if not id_number or not first_name or not last_name or not program_code:
            QMessageBox.warning(self, "Validation Error", "All fields are required!")
            return

        # Validate ID format (YYYY-NNNN)
        if len(id_number) != 9 or id_number[4] != '-':
            QMessageBox.warning(self, "Validation Error", "ID Number must be in YYYY-NNNN format!")
            return

        self.accept()

    def get_student_data(self):
        return {
            'id_number': self.id_number.text().strip(),
            'first_name': self.first_name.text().strip(),
            'last_name': self.last_name.text().strip(),
            'year_level': int(self.year_level.currentText()),
            'gender': self.gender.currentText(),
            'program_code': self.program_code.currentData()
        }