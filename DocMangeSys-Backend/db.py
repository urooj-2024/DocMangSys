import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="youruser",  
        password="youpass",  
        database="yourdb"
    )
