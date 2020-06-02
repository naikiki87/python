import sqlite3

# con = sqlite3.connect("D:/python/db_sqlite/kospi.db")
con = sqlite3.connect("./kospi.db")

cur = con.cursor()
# cur.execute("CREATE TABLE PhoneBook(Name text, PhoneNum text);")
# cur.execute("INSERT INTO PhoneBook Values('Derick', '010-1234-5678');")
cur.execute("SELECT * FROM PhoneBook")
for row in cur:
    print(row)

# con.commit()
# con.close()