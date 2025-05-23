import mysql.connector

class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin123",
            database="student_information_system"
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            if query.strip().lower().startswith("select"):
                return self.cursor.fetchall()
            self.connection.commit()
            # Return number of affected rows for DELETE/UPDATE/INSERT
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return -1

    def close(self):
        self.cursor.close()
        self.connection.close()