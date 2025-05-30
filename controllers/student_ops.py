from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QHeaderView
from PyQt6.QtCore import Qt
from dialogs import StudentDialog
from PyQt6.QtWidgets import QMessageBox, QDialog
import mysql.connector
import pymysql
from utils.shortcuts import unselect_all_rows
from utils import database

def load_students(db, students_table):
    students_table.setSortingEnabled(False) # Disable sorting to prevent issues while loading data
    
    query = """
    SELECT s.id_number, s.first_name, s.last_name, s.year_level, s.gender, 
           p.code as program_code, p.name as program_name
    FROM students s
    JOIN programs p ON s.program_code = p.code
    """
    students = db.execute_query(query)
    students_table.setRowCount(len(students))
    for row, student in enumerate(students):
        students_table.setItem(row, 0, QTableWidgetItem(student['id_number']))
        students_table.setItem(row, 1, QTableWidgetItem(student['first_name']))
        students_table.setItem(row, 2, QTableWidgetItem(student['last_name']))
        students_table.setItem(row, 3, QTableWidgetItem(str(student['year_level'])))
        students_table.setItem(row, 4, QTableWidgetItem(student['gender']))
        students_table.setItem(row, 5, QTableWidgetItem(student['program_code']))
        
    for row in range(students_table.rowCount()):
        for col in range(students_table.columnCount()):
            item = students_table.item(row, col)
            if item:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
    header = students_table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    students_table.setSortingEnabled(True) # Re-enable sorting after loading data

def delete_student(db, students_table, parent):
    selected_ranges = students_table.selectedRanges()
    if not selected_ranges:
        QMessageBox.warning(parent, "Warning", "Please select student(s) to delete.")
        return

    # Collect all selected row indices
    rows = set()
    for sel_range in selected_ranges:
        for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
            rows.add(row)
    rows = sorted(rows, reverse=True)  # Reverse so deleting doesn't mess up indices

    # Confirm deletion
    ids = [students_table.item(row, 0).text() for row in rows]
    reply = QMessageBox.question(
        parent, 'Confirm Delete',
        f"Are you sure you want to delete the selected student(s)?\n{', '.join(ids)}",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )

    if reply == QMessageBox.StandardButton.Yes:
        deleted_count = 0
        for id_number in ids:
            result = db.execute_query("DELETE FROM students WHERE id_number = %s", (id_number,))
            if result > 0:
                deleted_count += 1
        load_students(db, students_table)
        if deleted_count > 0:
            QMessageBox.information(parent, "Success", "Selected student(s) deleted successfully!")
        else:
            QMessageBox.warning(parent, "Warning", "No student(s) were deleted.")

import pymysql.err

def add_student(db, students_table, parent):
    programs = db.execute_query("SELECT code, name FROM programs")
    if not programs:
        QMessageBox.warning(parent, "Error", "No programs available. Please add a program first.")
        return

    dialog = StudentDialog(db, programs=programs, parent=parent)
    dialog.setObjectName("add_student_dialog")

    if dialog.exec() == QDialog.DialogCode.Accepted:
        student_data = dialog.get_student_data()

        # Check for duplicate ID Number
        existing = db.execute_query("SELECT id_number FROM students WHERE id_number = %s", (student_data['id_number'],))
        if existing:
            QMessageBox.warning(parent, "Duplicate Entry", f"Student ID '{student_data['id_number']}' already exists.")
            return

        query = """
        INSERT INTO students (id_number, first_name, last_name, year_level, gender, program_code)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        result = db.execute_query(query, (
            student_data['id_number'],
            student_data['first_name'],
            student_data['last_name'],
            student_data['year_level'],
            student_data['gender'],
            student_data['program_code']
        ))

        if result:
            load_students(db, students_table)
            QMessageBox.information(parent, "Success", "Student added successfully!")
        else:
            QMessageBox.warning(parent, "Error", "Failed to add student.")

def edit_student(db, students_table, parent):
    selected = students_table.selectedItems()
    if not selected:
        QMessageBox.warning(parent, "Warning", "Please select a student to edit.")
        return

    row = selected[0].row()
    original_id = students_table.item(row, 0).text()

    student = db.execute_query("SELECT * FROM students WHERE id_number = %s", (original_id,))
    if not student:
        QMessageBox.warning(parent, "Error", "Selected student not found.")
        return

    programs = db.execute_query("SELECT code, name FROM programs")
    dialog = StudentDialog(db, student=student[0], programs=programs, parent=parent)
    dialog.setObjectName("edit_student_dialog")

    if dialog.exec() == QDialog.DialogCode.Accepted:
        student_data = dialog.get_student_data()
        new_id = student_data['id_number']

        # Check for duplicate ID Number, excluding the current student
        if new_id != original_id:
            existing = db.execute_query("SELECT id_number FROM students WHERE id_number = %s", (new_id,))
            if existing:
                QMessageBox.warning(parent, "Duplicate Entry", f"Student ID '{new_id}' already exists.")
                return

        query = """
        UPDATE students 
        SET id_number = %s, first_name = %s, last_name = %s, year_level = %s, gender = %s, program_code = %s
        WHERE id_number = %s
        """
        result = None
        try:
            result = db.execute_query(query, (
                new_id,
                student_data['first_name'],
                student_data['last_name'],
                student_data['year_level'],
                student_data['gender'],
                student_data['program_code'],
                original_id
            ))
        except pymysql.err.IntegrityError as e:
            if "Duplicate entry" in str(e):
                QMessageBox.warning(parent, "Duplicate ID", f"Student ID '{new_id}' already exists.")
                return
            else:
                QMessageBox.critical(parent, "Database Error", str(e))
                return

        if result:
            load_students(db, students_table)
            # Reselect the updated row
            for row in range(students_table.rowCount()):
                if students_table.item(row, 0).text() == new_id:
                    students_table.selectRow(row)
                    break
            QMessageBox.information(parent, "Success", "Student updated successfully!")
        else:
            QMessageBox.warning(parent, "Error", "Failed to update student.")

        
def filter_students_table(table_widget, search_bar, search_by_combo):
    search_by = search_by_combo.lower()
    search_bar = search_bar.lower()

    for row in range(table_widget.rowCount()):
        match = False
        for col in range(table_widget.columnCount()):
            item = table_widget.item(row, col)
            if item:
                header_text = table_widget.horizontalHeaderItem(col).text().lower()
                if search_by == "all":
                    if search_bar in item.text().lower():
                        match = True
                        break
                elif header_text == search_by:
                    if search_bar in item.text().lower():
                        match = True
                        break
        table_widget.setRowHidden(row, not match)


                
    