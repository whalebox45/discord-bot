import csv
import sqlite3

conn = sqlite3.connect('card.db')
with open('output.csv', newline='',encoding='utf-8') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        if row:
            card_row = [row[3],row[5],row[7],row[9],row[11],row[13],row[15],row[17],row[19],row[21]]
            
            cur = conn.cursor()
            cur.execute('insert into Cards values(?,?,?,?,?,?,?,?,?,?)',card_row)
            conn.commit()