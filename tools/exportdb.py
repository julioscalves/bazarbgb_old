import datetime
import os
import sqlite3

con = sqlite3.connect('names.db')
cur = con.cursor()

now = datetime.datetime.now()

with open(f'boardgames_{now.hour}{now.minute}{now.second}{now.day}{now.month}{now.year}_export.txt', 'w', encoding='utf8') as names:

    boardgames = cur.execute('SELECT * FROM boardgames')

    for boardgame in boardgames:
        names.write(f'{boardgame[1]}|{boardgame[2]}\n')

con.commit()
con.close