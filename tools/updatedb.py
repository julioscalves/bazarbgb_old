import re
import os
import sqlite3

con = sqlite3.connect('names.db')
cur = con.cursor()

try:
    cur.execute('CREATE TABLE boardgames (id integer primary key, name text unique, tag text)')

except:
    pass
    
finally:

    with open('boardgames_140262982021_export.txt', 'r', encoding='utf8') as names:
        names = names.readlines()
        
        for name in names:
            name = name.strip().split('|')
            boardgame = re.sub(r'\([0-9]{4}\)', '', name[0]).strip()
            tag = name[1]

            print(boardgame)

            cur.execute(f"INSERT OR REPLACE INTO boardgames VALUES (NULL, :name, :tag) \
                          ON CONFLICT(name) DO UPDATE SET name=:name, tag=:tag" , {'name': boardgame, 'tag': tag,})

con.commit()
con.close