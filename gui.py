from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QStackedWidget,
    QHeaderView, QLineEdit, QSizePolicy, QSpacerItem, QLabel, QComboBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QFontDatabase, QPixmap
from utils import Database, add_shortcuts
from controllers import *
from pathlib import Path
import os
import mysql.connector


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("resources/icons/WindowIcon.svg"))
        self.db = Database()
        self.setWindowTitle("Student Information System")
        self.setGeometry(100, 100, 900, 600)
        self.setMinimumSize(1000, 600)
        
        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(150)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Add a vertical spacer at the top
        top_spacer = QSpacerItem(20, 3, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sidebar_layout.addItem(top_spacer)

        # Add logotype (logo image)
        logo_label = QLabel()
        logo_pixmap = QPixmap(str(Path(__file__).parent / "resources" / "icons" / "SSIS.png"))
        logo_label.setPixmap(
            logo_pixmap.scaled(QSize(100, 100), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        # Sidebar buttons
        self.students_btn = QPushButton(" Students")
        self.students_btn.setIcon(QIcon("resources/icons/Student.svg"))
        self.students_btn.setIconSize(QSize(24, 24))
        self.students_btn.setObjectName("SidebarButton")
        self.students_btn.setFixedHeight(40)
        self.students_btn.setFlat(True)
        self.students_btn.setCheckable(True)
        self.students_btn.clicked.connect(lambda: self.sidebar_navigate(0))
        
        self.programs_btn = QPushButton(" Programs")
        self.programs_btn.setIcon(QIcon("resources/icons/Program.svg"))
        self.programs_btn.setIconSize(QSize(24, 24))
        self.programs_btn.setObjectName("SidebarButton")
        self.programs_btn.setFixedHeight(40)
        self.programs_btn.setFlat(True)
        self.programs_btn.setCheckable(True)
        self.programs_btn.clicked.connect(lambda: self.sidebar_navigate(1))
        
        self.colleges_btn = QPushButton(" Colleges")
        self.colleges_btn.setIcon(QIcon("resources/icons/College.svg"))
        self.colleges_btn.setIconSize(QSize(24, 24))
        self.colleges_btn.setObjectName("SidebarButton")
        self.colleges_btn.setFixedHeight(40)
        self.colleges_btn.setFlat(True)
        self.colleges_btn.setCheckable(True)
        self.colleges_btn.clicked.connect(lambda: self.sidebar_navigate(2))

        sidebar_layout.addWidget(self.students_btn)
        sidebar_layout.addWidget(self.programs_btn)
        sidebar_layout.addWidget(self.colleges_btn)
        sidebar_layout.addStretch()

        # Main content area
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("MainStack")  # Add this line

        # Students tab
        self.students_tab = QWidget()
        self.setup_students_tab()
        self.stacked_widget.addWidget(self.students_tab)

        # Programs tab
        self.programs_tab = QWidget()
        self.setup_programs_tab()
        self.stacked_widget.addWidget(self.programs_tab)

        # Colleges tab
        self.colleges_tab = QWidget()
        self.setup_colleges_tab()
        self.stacked_widget.addWidget(self.colleges_tab)

        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)

        # Load initial data
        self.load_colleges()
        self.load_programs()
        self.load_students()

        self.students_icon = QIcon("resources/icons/Student.svg")
        self.students_icon_selected = QIcon("resources/icons/Student_selected.svg")
        self.programs_icon = QIcon("resources/icons/Program.svg")
        self.programs_icon_selected = QIcon("resources/icons/Program_selected.svg")
        self.colleges_icon = QIcon("resources/icons/College.svg")
        self.colleges_icon_selected = QIcon("resources/icons/College_selected.svg")

        self.students_btn.setIcon(self.students_icon)
        self.programs_btn.setIcon(self.programs_icon)
        self.colleges_btn.setIcon(self.colleges_icon)

        # Set initial sidebar button and stack index
        self.select_sidebar_button(self.students_btn)
        self.stacked_widget.setCurrentIndex(0)
    
        add_shortcuts(self)
    
    def setup_students_tab(self):
        layout = QVBoxLayout(self.students_tab)

        # Buttons, Search Bar and Search By
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(32, 24, 32, 0)
        self.student_search = QLineEdit()
        self.student_search.setObjectName("SearchBar")
        self.student_search.setPlaceholderText("Search students...")
        self.student_search.textChanged.connect(self.filter_students_table)
        self.student_search.returnPressed.connect(self.filter_students_table)
        self.student_search.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # <-- Add this line
        btn_layout.addWidget(self.student_search)

        self.Ssearch_by_label = QComboBox()
        self.Ssearch_by_label.setObjectName("searchBy")
        self.Ssearch_by_label.addItems(["All", "ID Number", "First Name", "Last Name", "Year Level", "Gender", "Program Code"])
        btn_layout.addWidget(self.Ssearch_by_label)
        
        self.add_student_btn = QPushButton("")
        self.add_student_btn.setObjectName("AddButton")
        self.add_student_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_student_btn.setIconSize(QSize(34, 34))
        self.add_student_btn.clicked.connect(self.add_student)
        self.add_student_btn.setToolTip("Add Student")
        
        self.edit_student_btn = QPushButton("")
        self.edit_student_btn.setObjectName("EditButton")
        self.edit_student_btn.setIconSize(QSize(34, 34))
        self.edit_student_btn.setIcon(QIcon("resources/icons/edit.png"))
        self.edit_student_btn.clicked.connect(self.edit_student)
        self.edit_student_btn.setToolTip("Edit Selected Student")
        
        self.delete_student_btn = QPushButton("")
        self.delete_student_btn.setObjectName("DeleteButton")
        self.delete_student_btn.setIconSize(QSize(34, 34))
        self.delete_student_btn.setIcon(QIcon("resources/icons/delete.png"))
        self.delete_student_btn.clicked.connect(self.delete_student)
        self.delete_student_btn.setToolTip("Delete Selected Student(s)")
        
        btn_layout.addWidget(self.add_student_btn)
        btn_layout.addWidget(self.edit_student_btn)
        btn_layout.addWidget(self.delete_student_btn)

        # Table
        self.students_table = QTableWidget()
        self.students_table.setSortingEnabled(True)
        self.students_table.setColumnCount(6)
        self.students_table.setHorizontalHeaderLabels([
            "ID Number", "First Name", "Last Name", "Year Level", "Gender", "Program"
        ])
        self.students_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.students_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.students_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        
        # Set column width to fit contents and stretch last column
        header = self.students_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.students_table.verticalHeader().setVisible(False)

        layout.addLayout(btn_layout)
        layout.addWidget(self.students_table)

    def filter_students_table(self):
        selected_field = self.Ssearch_by_label.currentText()
        query = self.student_search.text()
        filter_students_table(self.students_table, query, selected_field)

    def setup_programs_tab(self):
        layout = QVBoxLayout(self.programs_tab)

        # Buttons and Search Bar
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(32, 24, 32, 0)  # left, top, right, bottom
        self.program_search = QLineEdit()
        self.program_search.setObjectName("SearchBar")
        self.program_search.setPlaceholderText("Search programs...")
        self.program_search.textChanged.connect(self.filter_programs_table)
        self.program_search.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_layout.addWidget(self.program_search)

        self.Psearch_by_label = QComboBox()
        self.Psearch_by_label.setObjectName("searchBy")
        self.Psearch_by_label.addItems(["All", "Code", "Name", "College"])
        btn_layout.addWidget(self.Psearch_by_label)

        self.add_program_btn = QPushButton("")
        self.add_program_btn.setObjectName("AddButton")
        self.add_program_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_program_btn.setIconSize(QSize(34, 34))
        self.add_program_btn.clicked.connect(self.add_program)
        self.add_program_btn.setToolTip("Add Program")
        self.edit_program_btn = QPushButton("")
        self.edit_program_btn.setObjectName("EditButton")
        self.edit_program_btn.setIcon(QIcon("resources/icons/edit.png"))
        self.edit_program_btn.setIconSize(QSize(34, 34))
        self.edit_program_btn.clicked.connect(self.edit_program)
        self.edit_program_btn.setToolTip("Edit Selected Program")
        self.delete_program_btn = QPushButton("")
        self.delete_program_btn.setObjectName("DeleteButton")
        self.delete_program_btn.setIcon(QIcon("resources/icons/delete.png"))
        self.delete_program_btn.setIconSize(QSize(34, 34))
        self.delete_program_btn.clicked.connect(self.delete_program)
        self.delete_program_btn.setToolTip("Delete Selected Program(s)")

        btn_layout.addWidget(self.add_program_btn)
        btn_layout.addWidget(self.edit_program_btn)
        btn_layout.addWidget(self.delete_program_btn)

        # Table
        self.programs_table = QTableWidget()
        self.programs_table.setSortingEnabled(True)
        self.programs_table.setColumnCount(3)
        self.programs_table.setHorizontalHeaderLabels(["Code", "Name", "College"])
        self.programs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.programs_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.programs_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        
        header = self.programs_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.programs_table.verticalHeader().setVisible(False)


        layout.addLayout(btn_layout)
        layout.addWidget(self.programs_table)

    def filter_programs_table(self):
        selected_field = self.Psearch_by_label.currentText()
        query = self.program_search.text()
        filter_programs_table(self.programs_table, query, selected_field)

    def setup_colleges_tab(self):
        layout = QVBoxLayout(self.colleges_tab)

        # Buttons and Search Bar
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(32, 24, 32, 0)  # left, top, right, bottom
        self.college_search = QLineEdit()
        self.college_search.setObjectName("SearchBar")
        self.college_search.setPlaceholderText("Search colleges...")
        self.college_search.textChanged.connect(self.filter_colleges_table)
        self.college_search.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_layout.addWidget(self.college_search)
        
        self.Csearch_by_label = QComboBox()
        self.Csearch_by_label.setObjectName("searchBy")
        self.Csearch_by_label.addItems(["All", "Code", "Name"])
        self.Csearch_by_label.currentTextChanged.connect(self.sort_college_table)
        btn_layout.addWidget(self.Csearch_by_label)  

        self.add_college_btn = QPushButton("")
        self.add_college_btn.setObjectName("AddButton")
        self.add_college_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_college_btn.setIconSize(QSize(34, 34))
        self.add_college_btn.clicked.connect(self.add_college)
        self.add_college_btn.setToolTip("Add College")
        self.edit_college_btn = QPushButton("")
        self.edit_college_btn.setObjectName("EditButton")
        self.edit_college_btn.setIcon(QIcon("resources/icons/edit.png"))
        self.edit_college_btn.setIconSize(QSize(34, 34))
        self.edit_college_btn.clicked.connect(self.edit_college)
        self.edit_college_btn.setToolTip("Edit Selected College")
        self.delete_college_btn = QPushButton("")
        self.delete_college_btn.setObjectName("DeleteButton")
        self.delete_college_btn.setIcon(QIcon("resources/icons/delete.png"))
        self.delete_college_btn.setIconSize(QSize(34, 34))
        self.delete_college_btn.clicked.connect(self.delete_college)
        self.delete_college_btn.setToolTip("Delete Selected College(s)")
        
        btn_layout.addWidget(self.add_college_btn)
        btn_layout.addWidget(self.edit_college_btn)
        btn_layout.addWidget(self.delete_college_btn)

        # Table
        self.colleges_table = QTableWidget()
        self.colleges_table.setSortingEnabled(True)
        self.colleges_table.setColumnCount(2)
        self.colleges_table.setHorizontalHeaderLabels(["Code", "Name"])
        self.colleges_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.colleges_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.colleges_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        
        header = self.colleges_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.colleges_table.verticalHeader().setVisible(False)


        layout.addLayout(btn_layout)
        layout.addWidget(self.colleges_table)

    def sort_college_table(self, selected_text):
        column_map = {
            "Code": "code",
            "Name": "name",
        }

        column = column_map.get(selected_text)
        if column:
            # Call the external load_colleges function, passing db and table
            load_colleges(self.db, self.colleges_table, order_by_column=column)


    def filter_colleges_table(self):
        selected_field = self.Csearch_by_label.currentText()
        query = self.college_search.text()
        filter_colleges_table(self.colleges_table, query, selected_field)

    # Student CRUDL methods
    def load_students(self):
        load_students(self.db, self.students_table)
    
    def add_student(self):
        add_student(self.db, self.students_table, self)
    
    def edit_student(self):
        edit_student(self.db, self.students_table, self)
            
    def delete_student(self):
        delete_student(self.db, self.students_table, self)

    # Program CRUDL methods
    def load_programs(self):
        load_programs(self.db, self.programs_table)
    
    def add_program(self):
        add_program(self.db, self.programs_table, self)

    def edit_program(self):
        edit_program(self.db, self.programs_table, self)

    def delete_program(self):
        delete_program(self.db, self.programs_table, self)

    # College CRUDL methods
    def load_colleges(self):
        load_colleges(self.db, self.colleges_table)
    
    def add_college(self):
        add_college(self.db, self.colleges_table, self)

    def edit_college(self):
        edit_college(self.db, self.colleges_table, self)
                
    def delete_college(self):
        delete_college(self.db, self.colleges_table, self)

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)
        
    def select_sidebar_button(self, selected_btn):
        btn_icon_map = [
            (self.students_btn, self.students_icon, self.students_icon_selected),
            (self.programs_btn, self.programs_icon, self.programs_icon_selected),
            (self.colleges_btn, self.colleges_icon, self.colleges_icon_selected),
        ]
        for btn, icon, icon_selected in btn_icon_map:
            if btn is selected_btn:
                btn.setChecked(True)
                btn.setIcon(icon_selected)
            else:
                btn.setChecked(False)
                btn.setIcon(icon)

    def sidebar_navigate(self, index):
        btns = [self.students_btn, self.programs_btn, self.colleges_btn]
        self.select_sidebar_button(btns[index])
        self.stacked_widget.setCurrentIndex(index)

def load_font(app):
    # Determine font path
    font_dir = Path(__file__).parent / "resources" / "fonts"
    font_path = str(font_dir / "Roboto-Regular.ttf")
    
    # Verify font exists
    if not os.path.exists(font_path):
        print(f"Warning: Font not found at {font_path}")
        return
    
    # Load font
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        print("Warning: Failed to load Roboto font")
        return
    
    # Get font family name
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    
    # Set as default font
    app.setFont(QFont(font_family, 10))
