#!/usr/bin/python
import MySQLdb
import csv, sys
import html
import secrete as secrete
from tkinter import filedialog
from tkinter import *

root = Tk().withdraw()
filename =  filedialog.askopenfilename(initialdir = "/",title = "Select Contact File",filetypes = (("csv files","*.csv"),("all files","*.*")))
print(filename)

db = MySQLdb.connect(secrete.db_url,secrete.user_name,secrete.password,secrete.db)
cursor = db.cursor()

sql = "TRUNCATE TABLE contact"
try:
   # Execute the SQL command
   cursor.execute(sql)
   # Commit your changes in the database
   db.commit()
except:
   # Rollback in case there is any error
   print("delete fail")
   db.rollback()


add_data = ("INSERT INTO contact"
               "(            StartDate,EndDate,Status,IPAddress,Progress,Duration,Finished,RecordedDate,ResponseId,RecipientLastName,RecipientFirstName,RecipientEmail,ExternalReference,LocationLatitude,LocationLongitude,DistributionChannel,UserLanguage,Q2_1,Q3,Q4,Q4_11_TEXT,Q5_1,Q6,Q7,Q8,Q9,Q10_1,Q10_2,Q10_3,Q10_4,Q10_5,Q10_6,Q10_7,Q10_8,Q10_9,Q10_10,Q10_11,Q10_12,Q11_1,Q11_2,Q11_3,Q11_4,Q11_5,Q11_6,Q11_7,Q12_1,Q12_2,Q12_3,Q12_4,Q12_5,Q12_6,Q12_7,Q12_8,Q12_9,Q13_1,Q13_2,Q13_3,Q13_4,Q13_5,Q13_6,Q14_1,Q14_2,Q14_3,Q14_4,Q14_5,Q14_6,name,uid,cid) "
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
            StartDate
            EndDate
            Status
            IPAddress
            Progress
            Duration (in seconds)
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
            Q3
            Q4
            Q4_11_TEXT
            Q5_1
            Q6
            Q7
            Q8
            Q9
            Q10_1
            Q10_2
            Q10_3
            Q10_4
            Q10_5
            Q10_6
            Q10_7
            Q10_8
            Q10_9
            Q10_10
            Q10_11
            Q10_12
            Q11_1
            Q11_2
            Q11_3
            Q11_4
            Q11_5
            Q11_6
            Q11_7
            Q12_1
            Q12_2
            Q12_3
            Q12_4
            Q12_5
            Q12_6
            Q12_7
            Q12_8
            Q12_9
            Q13_1
            Q13_2
            Q13_3
            Q13_4
            Q13_5
            Q13_6
            Q14_1
            Q14_2
            Q14_3
            Q14_4
            Q14_5
            Q14_6
            name
            uid
            cid
            StartDate,EndDate,Status,IPAddress,Progress,Duration,Finished,RecordedDate,ResponseId,RecipientLastName,RecipientFirstName,RecipientEmail,ExternalReference,LocationLatitude,LocationLongitude,DistributionChannel,UserLanguage,Q2_1,Q3,Q4,Q4_11_TEXT,Q5_1,Q6,Q7,Q8,Q9,Q10_1,Q10_2,Q10_3,Q10_4,Q10_5,Q10_6,Q10_7,Q10_8,Q10_9,Q10_10,Q10_11,Q10_12,Q11_1,Q11_2,Q11_3,Q11_4,Q11_5,Q11_6,Q11_7,Q12_1,Q12_2,Q12_3,Q12_4,Q12_5,Q12_6,Q12_7,Q12_8,Q12_9,Q13_1,Q13_2,Q13_3,Q13_4,Q13_5,Q13_6,Q14_1,Q14_2,Q14_3,Q14_4,Q14_5,Q14_6,name,uid,cid
            """

            cursor.execute(add_data, data)

    except csv.Error as e:
        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

db.commit()
cursor.close()
# disconnect from server
db.close()
