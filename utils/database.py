import pymysql
import pymysql.cursors

class Database:
    def __init__(self):
        self.connection = pymysql.connect(
            host="localhost",
            user="root",
            password="admin123",
            database="student_information_system",
            cursorclass=pymysql.cursors.DictCursor
        )

    def fetch_one(self, query, params=()):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                if query.strip().lower().startswith("select"):
                    return cursor.fetchall()
                self.connection.commit()
                return cursor.rowcount
        except pymysql.MySQLError as err:
            print(f"Error: {err}")
            return -1

    def close(self):
        self.connection.close()


# import mysql.connector
# import pymysql
# import pymysql.cursors

# class Database:
#     def __init__(self):
#         self.connection = pymysql.connect(
#             host="localhost",
#             user="root",
#             password="admin123",
#             database="student_information_system"
#         )
#         self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
#         # self.connection = mysql.connector.connect(
#         #     host="localhost",
#         #     user="root",
#         #     password="admin123",
#         #     database="student_information_system"
#         # )
#         # self.cursor = self.connection.cursor(dictionary=True)

#     def fetch_one(self, query, params=()):
#         with self.cursor as cursor:
#             cursor.execute(query, params)
#             return cursor.fetchone()
    
#     def execute_query(self, query, params=None):
#         try:
#             self.cursor.execute(query, params or ())
#             if query.strip().lower().startswith("select"):
#                 return self.cursor.fetchall()
#             self.connection.commit()
#             # Return number of affected rows for DELETE/UPDATE/INSERT
#             return self.cursor.rowcount
#         except mysql.connector.Error as err:
#             print(f"Error: {err}")
#             return -1

#     def close(self):
#         self.cursor.close()
#         self.connection.close()
        
    