from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QHeaderView
from PyQt6.QtCore import Qt
from dialogs import ProgramDialog
from PyQt6.QtWidgets import QMessageBox, QDialog
import pymysql
from pymysql.err import IntegrityError

def load_programs(db, programs_table):
        programs_table.setSortingEnabled(False)  # Disable sorting to prevent issues while loading data
    
        query = """
        SELECT p.code, p.name, c.code as college_code, c.name as college_name
        FROM programs p
        JOIN colleges c ON p.college_code = c.code
        """
        programs = db.execute_query(query)
        programs_table.setRowCount(len(programs))
        for row, program in enumerate(programs):
            programs_table.setItem(row, 0, QTableWidgetItem(program['code']))
            programs_table.setItem(row, 1, QTableWidgetItem(program['name']))
            programs_table.setItem(row, 2, QTableWidgetItem(program['college_code']))

        # Center align the text in the table
        for row in range(programs_table.rowCount()):
            for col in range(programs_table.columnCount()):
                item = programs_table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header = programs_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        programs_table.setSortingEnabled(True)  # Re-enable sorting after loading data

def delete_program(db, programs_table, parent):
    selected_ranges = programs_table.selectedRanges()
    if not selected_ranges:
        QMessageBox.warning(parent, "Warning", "Please select program(s) to delete.")
        return

    rows = set()
    for sel_range in selected_ranges:
        for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
            rows.add(row)
    rows = sorted(rows, reverse=True)

    codes = [programs_table.item(row, 0).text() for row in rows]
    reply = QMessageBox.question(
        parent, 'Confirm Delete',
        f"Are you sure you want to delete the selected program(s)?\n{', '.join(codes)}",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
        deleted_count = 0
        for code in codes:
            result = db.execute_query("DELETE FROM programs WHERE code = %s", (code,))
            if result > 0:
                deleted_count += 1
        load_programs(db, programs_table)
        if hasattr(parent, 'load_students'):
            parent.load_students()
        if deleted_count > 0:
            QMessageBox.information(parent, "Success", "Selected program(s) deleted successfully!")
        else:
            QMessageBox.warning(parent, "Warning", "No program(s) were deleted.")

def add_program(db, programs_table, parent):
    colleges = db.execute_query("SELECT code, name FROM colleges")
    if not colleges:
        QMessageBox.warning(parent, "Error", "No colleges available. Please add a college first.")
        return

    dialog = ProgramDialog(db, colleges=colleges, parent=parent)
    dialog.setObjectName("add_program_dialog")
    if dialog.exec() == QDialog.DialogCode.Accepted:
        program_data = dialog.get_program_data()
        query = "INSERT INTO programs (code, name, college_code) VALUES (%s, %s, %s)"
        try:
            if db.execute_query(query, (
                program_data['code'],
                program_data['name'],
                program_data['college_code']
            )):
                load_programs(db, programs_table)
                if hasattr(parent, 'load_students'):
                    parent.load_students()
                QMessageBox.information(parent, "Success", "Program added successfully!")
            else:
                QMessageBox.warning(parent, "Error", "Failed to add program.")
        except IntegrityError as e:
            if "Duplicate entry" in str(e):
                QMessageBox.warning(parent, "Duplicate Code", f"Program code '{program_data['code']}' already exists.")
            else:
                QMessageBox.critical(parent, "Database Error", str(e))

# def add_program(db, programs_table, parent):
#     colleges = db.execute_query("SELECT code, name FROM colleges")
#     if not colleges:
#         QMessageBox.warning(parent, "Error", "No colleges available. Please add a college first.")
#         return

#     dialog = ProgramDialog(db, colleges=colleges, parent=parent)
#     dialog.setObjectName("add_program_dialog")
#     if dialog.exec() == QDialog.DialogCode.Accepted:
#         program_data = dialog.get_program_data()
#         query = "INSERT INTO programs (code, name, college_code) VALUES (%s, %s, %s)"
#         if db.execute_query(query, (
#             program_data['code'],
#             program_data['name'],
#             program_data['college_code']
#         )):
#             load_programs(db, programs_table)
#             if hasattr(parent, 'load_students'):
#                 parent.load_students()
#             QMessageBox.information(parent, "Success", "Program added successfully!")
#         else:
#             QMessageBox.warning(parent, "Error", "Failed to add program.")

def edit_program(db, programs_table, parent):
    selected = programs_table.selectedItems()
    if not selected:
        QMessageBox.warning(parent, "Warning", "Please select a program to edit.")
        return

    row = selected[0].row()
    original_code = programs_table.item(row, 0).text()
    
    program = db.execute_query("SELECT * FROM programs WHERE code = %s", (original_code,))
    if not program:
        QMessageBox.warning(parent, "Error", "Selected program not found.")
        return

    colleges = db.execute_query("SELECT code, name FROM colleges")
    dialog = ProgramDialog(db, program=program[0], colleges=colleges, parent=parent)
    dialog.setObjectName("edit_program_dialog")
    if dialog.exec() == QDialog.DialogCode.Accepted:
        program_data = dialog.get_program_data()
        query = "UPDATE programs SET code = %s, name = %s, college_code = %s WHERE code = %s"
        try:
            if db.execute_query(query, (
                program_data['code'],
                program_data['name'],
                program_data['college_code'],
                original_code
            )):
                from .program_ops import load_programs
                load_programs(db, programs_table)

                for row in range(programs_table.rowCount()):
                    if programs_table.item(row, 0).text() == program_data['code']:
                        programs_table.selectRow(row)
                        break

                if hasattr(parent, 'load_students'):
                    parent.load_students()

                QMessageBox.information(parent, "Success", "Program updated successfully!")
            else:
                QMessageBox.warning(parent, "Error", "Failed to update program.")
        except IntegrityError as e:
            if "Duplicate entry" in str(e):
                QMessageBox.warning(parent, "Duplicate Code", f"Program code '{program_data['code']}' already exists.")
            else:
                QMessageBox.critical(parent, "Database Error", str(e))

# def filter_programs_table(table_widget, search_bar, search_by_combo):
#     search_text = search_bar.text().lower()
#     search_by = search_by_combo.currentText().lower()
    
#     for row in range(table_widget.rowCount()):
#         match = False
#         for col in range(table_widget.columnCount()):
#             item = table_widget.item(row,col)
#             if item:
#                 header_text = table_widget.horizontalHeaderItem(col).text().lower()
#                 if search_by == "gender" and header_text == "gender":
#                     if search_text in item.text().lower():
#                         match = True
#                         break
#                 elif search_by == "all" or header_text == search_by:
#                     if search_text in item.text().lower():
#                         match = True
#                         break
#             table_widget.setRowHidden(row, not match)

def filter_programs_table(table_widget, search_bar, search_by_combo):
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
