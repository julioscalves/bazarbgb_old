import os
import sqlite3

con = sqlite3.connect('names.db')
cur = con.cursor()

try:
    cur.execute('CREATE TABLE boardgames (id integer primary key, name text unique, tag text)')

except:
    pass
    
finally:
    with open('boardgames_names.txt', 'r', encoding='utf8') as names:
        names = names.readlines()
        
        for name in names:
            name = name.strip().split('|')
            cur.execute(f"INSERT OR REPLACE INTO boardgames VALUES (NULL, :name, :tag) \
                          ON CONFLICT(name) DO UPDATE SET name=:name, tag=:tag" , {'name': name[0], 'tag': name[1],})

con.commit()
con.close