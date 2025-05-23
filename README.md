# Student Information System V2

A modern, themeable Student Information System built with **PyQt6** and **MySQL**.  
This application allows you to manage students, programs, and colleges with a user-friendly GUI, advanced search, sorting, and multi-selection features.

---

## Features

- **Student, Program, and College Management**
  - Add, edit, delete, and search students, programs, and colleges
  - Multi-row selection and deletion
  - Edit dialogs with validation and themed appearance

- **Modern UI**
  - Custom sidebar with icons and selection highlight
  - Themed tables, dialogs, tooltips, and message boxes
  - Responsive layouts and accent color support

- **Advanced Table Features**
  - Clickable, sortable table headers
  - Search bars with placeholder and icon
  - Selection highlighting and keyboard shortcuts

- **Database Integration**
  - Uses MySQL for persistent storage
  - All CRUD operations are reflected in the database

---

## Requirements

- Python 3.8+
- [PyQt6](https://pypi.org/project/PyQt6/)
- [mysql-connector-python](https://pypi.org/project/mysql-connector-python/)
- MySQL Server (with a database named `student_information_system`)

---

## Setup

1. **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd V2.7
    ```

2. **Install dependencies:**
    ```bash
    pip install PyQt6 mysql-connector-python
    ```

3. **Set up the MySQL database:**
    - Create a database named `student_information_system`.
    - Create the required tables (`students`, `programs`, `colleges`).  
      Example schema:
      ```sql
      CREATE TABLE colleges (
          code VARCHAR(10) PRIMARY KEY,
          name VARCHAR(100) NOT NULL
      );

      CREATE TABLE programs (
          code VARCHAR(10) PRIMARY KEY,
          name VARCHAR(100) NOT NULL,
          college_code VARCHAR(10),
          FOREIGN KEY (college_code) REFERENCES colleges(code) ON DELETE CASCADE
      );

      CREATE TABLE students (
          id_number VARCHAR(20) PRIMARY KEY,
          first_name VARCHAR(100) NOT NULL,
          last_name VARCHAR(100) NOT NULL,
          year_level INT NOT NULL,
          gender VARCHAR(10) NOT NULL,
          program_code VARCHAR(10),
          FOREIGN KEY (program_code) REFERENCES programs(code) ON DELETE CASCADE
      );
      ```

4. **Configure database credentials:**
    - Edit `utils/database.py` if your MySQL username, password, or host are different.

5. **Run the application:**
    ```bash
    python main.py
    ```

---

## Project Structure

```
V2.7/
│
├── controllers/         # CRUD logic for students, programs, colleges
├── dialogs/             # Custom dialog windows for editing/adding
├── resources/           # Icons and fonts
│   ├── icons/
│   └── fonts/
├── utils/               # Database, shortcuts, and style.qss
├── main.py              # Application entry point
├── gui.py               # Main window and UI layout
└── README.md
```

---

## Customization

- **Theme & Colors:**  
  Edit `utils/style.qss` to change the application's appearance.

- **Icons:**  
  Replace SVG/PNG files in `resources/icons/` for your own look.

- **Fonts:**  
  Place your preferred font in `resources/fonts/` and update the QSS if needed.

---

## Keyboard Shortcuts

- **Escape:** Unselect all rows in the current table.

---

## Troubleshooting

- **"Could not parse application stylesheet":**  
  Check `style.qss` for syntax errors (no `//` comments, use `/* ... */`).

- **Database connection errors:**  
  Ensure MySQL is running and credentials in `utils/database.py` are correct.

- **Missing icons or fonts:**  
  Make sure all files in `resources/icons/` and `resources/fonts/` exist.

---

## License

This project is for educational purposes.  
Feel free to use and modify it for your own needs.

---