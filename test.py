import sqlite3 as sql
import json

tags = ["2026","slim jims","pond water"]

conn = sql.connect("booty.db")
conn.execute("CREATE TABLE IF NOT EXISTS tabo (rowid INTEGER PRIMARY KEY, tags JSON)")
conn.execute("INSERT INTO tabo VALUES (NULL, ?)", json.dumps(tags) )
conn.commit()