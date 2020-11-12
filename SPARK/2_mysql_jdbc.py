from errno import errorcode
import mysql.connector

config = {
    'user': 'root',
    'password': 'Elql27!^',
    'host': '165.132.105.40',
    'database': 'projectBigdata',
    'raise_on_warnings': True,
  }

try:
    # cnx = mysql.connector.connect(user='root', password='Elql27!^', host='165.132.105.40', database='projectBigdata')
    cnx = mysql.connector.connect(**config)

    cursor = cnx.cursor()
    query = ("SELECT * from testdata")

    cursor.execute(query)
    for i in cursor :
        print(i)
    cursor.close()
    cnx.close()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exists")
    else:
        print(err)
else:
    cnx.close()