import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # Your MySQL username
        password='sqm#@9806',  # Your MySQL password
        database='Mbshop'  # Your database name
    )
    return connection
