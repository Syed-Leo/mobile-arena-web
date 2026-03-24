import mysql.connector as sql

con = sql.connect(
    host="localhost",
    
    database="Project"
)

cur = con.cursor()
