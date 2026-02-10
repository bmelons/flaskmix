import sqlite3 as sql
import json
import time
from math import floor

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

tags = ["2026","slim jims","pond wahter"]
tags2 = ["stump","gruntilda","2025 and half"]
jtags = json.dumps(tags2)
# print(jtags)

def getTimePublished():
    return floor(time.time())

def EpochToTimestamp(secs):
    return time.strftime("%B %d, %Y %I:%M %p",time.localtime(secs))

conn = sql.connect("booty.db")
conn.row_factory = dict_factory
conn.execute("CREATE TABLE IF NOT EXISTS tabo (rowid INTEGER PRIMARY KEY, tags JSON, time_published BIGINT)")
# conn.execute("INSERT INTO tabo VALUES (NULL, json(?),?)", (jtags,getTimePublished()))

all_items = conn.execute("SELECT * FROM tabo").fetchall()
for i in all_items:
    # print(i)
    stamp = EpochToTimestamp(i.get("time_published"))
    print(stamp)

conn.commit()