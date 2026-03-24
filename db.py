import mysql.connector as sql

con = sql.connect(
    host="localhost",
    user="root",
    passwd="root123",
    database="Project"
)

cur = con.cursor()
