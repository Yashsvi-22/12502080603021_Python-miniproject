
import mysql.connector
from mysql.connector import Error


def get_connection():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3307,
            user="root",
            password="",
            database="studyflow"
        )
        return connection

    except Error as error:
        print("Database connection failed:", error)
        return None


if __name__ == "__main__":
    connection = get_connection()

    if connection and connection.is_connected():
        print("StudyFlow database connected successfully!")
        print("Database:", connection.database)
        connection.close()
        print("Connection closed.")
    else:
        print("Please check your MySQL settings.")
