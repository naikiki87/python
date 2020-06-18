import sqlite3
import pandas as pd

# print(sqlite3.version)

# conn = sqlite3.connect("test.db")
# cur = conn.cursor()
# cur.execute("select * from customer")

# rows = cur.fetchall()
# for row in rows:
#     print(row)

# conn.close()

df = pd.DataFrame(columns = ['id', 'val'])
idx = 0

for i in range(10) :
    idx = len(df)
    df.loc[idx] = [i, i*10]

conn = sqlite3.connect("test.db")
df.to_sql("dftest", conn, if_exists="replace", index=False)


with conn:
    cur = conn.cursor()
    cur.execute("select * from dftest")
    rows = cur.fetchall()

    for row in rows:
        print(row)



# query = "select * from dftest where id= :Id"
# query = "select * from dftest where id= ?"
# cur.execute(query, {"Id" : 2})
# cur.execute(query, "2")
# cur.execute("select * from dftest where id = ?")

# rows = cur.fetchall()
# for row in rows:
#     print(row)

# conn.close()