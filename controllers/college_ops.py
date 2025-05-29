from dialogs import CollegeDialog
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QDialog, QHeaderView
from PyQt6.QtCore import Qt
import pymysql
from pymysql.err import IntegrityError

def load_colleges(db, colleges_table, order_by_column=None):
    colleges_table.setSortingEnabled(False)

    query = "SELECT code, name FROM colleges"
    if order_by_column in ['code', 'name']:
        query += f" ORDER BY {order_by_column} ASC"

    colleges = db.execute_query(query)

    colleges_table.setRowCount(len(colleges))
    for row, college in enumerate(colleges):
        colleges_table.setItem(row, 0, QTableWidgetItem(college['code']))
        colleges_table.setItem(row, 1, QTableWidgetItem(college['name']))

    for row in range(colleges_table.rowCount()):
        for col in range(colleges_table.columnCount()):
            item = colleges_table.item(row, col)
            if item:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    header = colleges_table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    colleges_table.setSortingEnabled(True)


# def load_colleges(db, colleges_table):
#         colleges_table.setSortingEnabled(False)  # Disable sorting to prevent issues while loading data
    
#         colleges = db.execute_query("SELECT code, name FROM colleges")
        
#         colleges_table.setRowCount(len(colleges))
#         for row, college in enumerate(colleges):
#             colleges_table.setItem(row, 0, QTableWidgetItem(college['code']))
#             colleges_table.setItem(row, 1, QTableWidgetItem(college['name']))

#         # Center all cells
#         for row in range(colleges_table.rowCount()):
#             for col in range(colleges_table.columnCount()):
#                 item = colleges_table.item(row, col)
#                 if item:
#                     item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

#         header = colleges_table.horizontalHeader()
#         header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
#         colleges_table.setSortingEnabled(True)  # Re-enable sorting after loading data
        
def delete_college(db, colleges_table, parent):
    selected_ranges = colleges_table.selectedRanges()
    if not selected_ranges:
        QMessageBox.warning(parent, "Warning", "Please select college(s) to delete.")
        return

    rows = set()
    for sel_range in selected_ranges:
        for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
            rows.add(row)
    rows = sorted(rows, reverse=True)

    codes = [colleges_table.item(row, 0).text() for row in rows]
    reply = QMessageBox.question(
        parent, 'Confirm Delete',
        f"Are you sure you want to delete the selected college(s)?\n{', '.join(codes)}",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
        deleted_count = 0
        for code in codes:
            result = db.execute_query("DELETE FROM colleges WHERE code = %s", (code,))
            if result > 0:
                deleted_count += 1
        load_colleges(db, colleges_table)
        if deleted_count > 0:
            QMessageBox.information(parent, "Success", "Selected college(s) deleted successfully!")
        else:
            QMessageBox.warning(parent, "Warning", "No college(s) were deleted.")

def add_college(db, colleges_table, parent):
    dialog = CollegeDialog(db, parent=parent)
    dialog.setObjectName("add_college_dialog")
    if dialog.exec() == QDialog.DialogCode.Accepted:
        college_data = dialog.get_college_data()
        query = "INSERT INTO colleges (code, name) VALUES (%s, %s)"
        try:
            if db.execute_query(query, (
                college_data['code'],
                college_data['name']
            )):
                load_colleges(db, colleges_table)
                if hasattr(parent, 'load_programs'):
                    parent.load_programs()
                QMessageBox.information(parent, "Success", "College added successfully!")
            else:
                QMessageBox.warning(parent, "Error", "Failed to add college.")
        except IntegrityError as e:
            if "Duplicate entry" in str(e):
                QMessageBox.warning(parent, "Duplicate Code", f"College code '{college_data['code']}' already exists.")
            else:
                QMessageBox.critical(parent, "Database Error", str(e))

# def add_college(db, colleges_table, parent):
#     dialog = CollegeDialog(db, parent=parent)
#     dialog.setObjectName("add_college_dialog")
#     if dialog.exec() == QDialog.DialogCode.Accepted:
#         college_data = dialog.get_college_data()
#         query = "INSERT INTO colleges (code, name) VALUES (%s, %s)"
#         if db.execute_query(query, (
#             college_data['code'],
#             college_data['name']
#         )):
#             load_colleges(db, colleges_table)
#             if hasattr(parent, 'load_programs'):
#                 parent.load_programs()
#             QMessageBox.information(parent, "Success", "College added successfully!")
#         else:
#             QMessageBox.warning(parent, "Error", "Failed to add college.")

def edit_college(db, colleges_table, parent):
    selected = colleges_table.selectedItems()
    if not selected:
        QMessageBox.warning(parent, "Warning", "Please select a college to edit.")
        return

    row = selected[0].row()
    original_code = colleges_table.item(row, 0).text()
    
    college = db.execute_query("SELECT * FROM colleges WHERE code = %s", (original_code,))
    if not college:
        QMessageBox.warning(parent, "Error", "Selected college not found.")
        return
    
    dialog = CollegeDialog(db, college=college[0], parent=parent)
    dialog.setObjectName("edit_college_dialog")
    if dialog.exec() == QDialog.DialogCode.Accepted:
        college_data = dialog.get_college_data()
        query = "UPDATE colleges SET code = %s, name = %s WHERE code = %s"
        try:
            if db.execute_query(query, (
                college_data['code'],
                college_data['name'],
                original_code
            )):
                load_colleges(db, colleges_table)
                
                # Select the updated row
                for row in range(colleges_table.rowCount()):
                    if colleges_table.item(row, 0).text() == college_data['code']:
                        colleges_table.selectRow(row)
                        break
                if hasattr(parent, 'load_programs'):
                    parent.load_programs()
                QMessageBox.information(parent, "Success", "College updated successfully!")
            else:
                QMessageBox.warning(parent, "Error", "Failed to update college.")
        except IntegrityError as e:
            if "Duplicate entry" in str(e):
                QMessageBox.warning(parent, "Duplicate Code", f"College code '{college_data['code']}' already exists.")
            else:
                QMessageBox.critical(parent, "Database Error", str(e))

# def edit_college(db, colleges_table, parent):
#     selected = colleges_table.selectedItems()
#     if not selected:
#         QMessageBox.warning(parent, "Warning", "Please select a college to edit.")
#         return

#     row = selected[0].row()
#     original_code = colleges_table.item(row, 0).text()
    
#     college = db.execute_query("SELECT * FROM colleges WHERE code = %s", (original_code,))
#     if not college:
#         QMessageBox.warning(parent, "Error", "Selected college not found.")
#         return
    
#     dialog = CollegeDialog(db, college=college[0], parent=parent)
#     dialog.setObjectName("edit_college_dialog")
#     if dialog.exec() == QDialog.DialogCode.Accepted:
#         college_data = dialog.get_college_data()
#         query = "UPDATE colleges SET code = %s, name = %s WHERE code = %s"
#         if db.execute_query(query, (
#             college_data['code'],
#             college_data['name'],
#             original_code
#         )):
#             load_colleges(db, colleges_table)
            
#             # --- Select the edited college row ---
#             for row in range(colleges_table.rowCount()):
#                 if colleges_table.item(row, 0).text() == college_data['code']:
#                     colleges_table.selectRow(row)
#                     break
#             if hasattr(parent, 'load_programs'):
#                 parent.load_programs()
#             QMessageBox.information(parent, "Success", "College updated successfully!")
#         else:
#             QMessageBox.warning(parent, "Error", "Failed to update college.")

def filter_colleges_table(table_widget, search_bar, search_by_combo):
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

# def filter_colleges_table(table_widget, search_bar, search_by_combo):
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