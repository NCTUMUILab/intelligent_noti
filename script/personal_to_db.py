#!/usr/bin/python
import MySQLdb
import csv, sys
import html
import secrete as secrete
from tkinter import filedialog
from tkinter import *

root = Tk().withdraw()
filename =  filedialog.askopenfilename(initialdir = "/",title = "Select Personal File",filetypes = (("csv files","*.csv"),("all files","*.*")))
print(filename)

db = MySQLdb.connect(secrete.db_url,secrete.user_name,secrete.password,secrete.db)
cursor = db.cursor()

sql = "TRUNCATE TABLE personal"
try:
   # Execute the SQL command
   cursor.execute(sql)
   # Commit your changes in the database
   db.commit()
except:
   # Rollback in case there is any error
   print("delete fail")
   db.rollback()


add_data = ("INSERT INTO personal"
               "(StartDate,EndDate,Status,IPAddress,Progress,Duration,Finished,RecordedDate,ResponseId,RecipientLastName,RecipientFirstName,RecipientEmail,ExternalReference,LocationLatitude,LocationLongitude,DistributionChannel,UserLanguage,Q2_1,Q2_2,Q2_3,Q2_4,Q2_5,Q2_6,Q2_7,Q2_8,Q2_9,Q2_10,Q2_11,Q2_12,Q2_13,Q2_14,Q2_15,Q2_16,Q2_17,Q2_18,Q2_19,Q3_1,Q3_2,Q3_3,Q3_4,Q3_5,Q3_6,Q3_7,Q3_8,Q3_9,Q3_10,Q3_11,Q3_12,Q3_13,Q3_14,Q3_15,Q3_16,Q3_17,Q3_18,Q3_19,Q3_20,Q4_1,Q4_2,Q4_3,Q4_4,Q4_5,Q4_6,Q4_7,Q4_8,Q4_9,Q4_10,name,uid,name_Topics) "
               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")

count = 0
with open(filename, 'r') as f:
    reader = csv.reader(f)
    try:
        for row in reader:
            if(count<3):
                count = count + 1
                continue
            data=(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22],row[23],row[24],row[25],row[26],row[27],row[28],row[29],row[30],row[31],row[32],row[33],row[34],row[35],row[36],row[37],row[38],row[39],row[40],row[41],row[42],row[43],row[44],row[45],row[46],row[47],row[48],row[49],row[50],row[51],row[52],row[53],row[54],row[55],row[56],row[57],row[58],row[59],row[60],row[61],row[62],row[63],row[64],row[65],html.unescape(row[66]),row[67],row[68])
            # print(data)
            """
            id
            StartDate
            EndDate
            Status
            IPAddress
            Progress
            Duration
            Finished
            RecordedDate
            ResponseId
            RecipientLastName
            RecipientFirstName
            RecipientEmail
            ExternalReference
            LocationLatitude
            LocationLongitude
            DistributionChannel
            UserLanguage
            Q2_1
            Q2_2
            Q2_3
            Q2_4
            Q2_5
            Q2_6
            Q2_7
            Q2_8
            Q2_9
            Q2_10
            Q2_11
            Q2_12
            Q2_13
            Q2_14
            Q2_15
            Q2_16
            Q2_17
            Q2_18
            Q2_19
            Q3_1
            Q3_2
            Q3_3
            Q3_4
            Q3_5
            Q3_6
            Q3_7
            Q3_8
            Q3_9
            Q3_10
            Q3_11
            Q3_12
            Q3_13
            Q3_14
            Q3_15
            Q3_16
            Q3_17
            Q3_18
            Q3_19
            Q3_20
            Q4_1
            Q4_2
            Q4_3
            Q4_4
            Q4_5
            Q4_6
            Q4_7
            Q4_8
            Q4_9
            Q4_10
            name
            uid
            name_Topics
            """

            cursor.execute(add_data, data)

    except csv.Error as e:
        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

db.commit()
cursor.close()
# disconnect from server
db.close()
