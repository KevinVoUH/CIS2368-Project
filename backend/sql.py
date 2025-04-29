#Sourced from class notes; specifically week 3 notes
import mysql.connector
from mysql.connector import Error

def DBconnection(hostname, uname, pwd, dbname):
    con = None
    try:
        con = mysql.connector.connect(
            host = hostname,
            user = uname,
            password = pwd,
            database = dbname
        )
        print("Connection successful")
    except Error as e:
        print("Connection unsuccessful due to Error ", e)
    return con

# Execute query function to read the rows from table
def execute_read_query(con, sql):
    mycursor = con.cursor(dictionary=True)
    rows = None
    try:
        mycursor.execute(sql)
        rows = mycursor.fetchall()
        return rows
    except Error as e:
        print("Error is: ", e)

# Execute query function to insert the rows into table
def execute_update_query(con, sql):
    mycursor = con.cursor()
    try:
        mycursor.execute(sql)
        con.commit()
        print("DB updated successfully")
    except Error as e:
        print("Error is : ", e)
        