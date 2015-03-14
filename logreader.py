import csv
import MySQLdb
import datetime

db = MySQLdb.connect('localhost', 'usbusr', 'reward', 'usb_events')

cursor = db.cursor()

csv_data = csv.reader(file('/var/log/testfile'))

start_row = 0

cur_row = 0
try:
    for row in csv_data:
        if cur_row >= start_row:
            dflnm, dhash, edflnm, edfhash, hnm, dt = row
            newdt = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            sql = "INSERT INTO usb_events.kusbwrlog (hname, desthash, destfilenm, filehash, execdfilenm, dttime) \
                    VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (hnm, dhash, dflnm, edfhash, edflnm, newdt)
            print sql
            cursor.execute(sql)

         # Other processing if necessary
        cur_row += 1

    db.commit()
except:
    db.rollback()
db.close()
