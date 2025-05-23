from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QMessageBox

class ProgramDialog(QDialog):
    def __init__(self, db, program=None, colleges=None, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(400)
        self.db = db
        self.program = program
        self.setWindowTitle("Add Program" if not program else "Edit Program")
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

        # College
        self.college_code = QComboBox()
        self.college_code.setObjectName("FormComboBox")
        if colleges:
            for college in colleges:
                self.college_code.addItem(f"{college['code']} - {college['name']}", college['code'])
        layout.addRow("College:", self.college_code)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.setObjectName("FormButtonBox")
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if program:
            self.load_program_data()

    def load_program_data(self):
        self.code.setText(self.program['code'])
        self.name.setText(self.program['name'])
        
        # Find the index of the program's college
        index = self.college_code.findData(self.program['college_code'])
        if index >= 0:
            self.college_code.setCurrentIndex(index)

    def validate_and_accept(self):
        code = self.code.text().strip()
        name = self.name.text().strip()
        college_code = self.college_code.currentData()

        if not code or not name or not college_code:
            QMessageBox.warning(self, "Validation Error", "All fields are required!")
            return

        self.accept()

    def get_program_data(self):
        return {
            'code': self.code.text().strip(),
            'name': self.name.text().strip(),
            'college_code': self.college_code.currentData()
        }
