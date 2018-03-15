#!/usr/bin/python
import MySQLdb
import csv, sys
import html

db = MySQLdb.connect("ec2-18-220-229-235.us-east-2.compute.amazonaws.com","root","whomatter","who_matter2" )
cursor = db.cursor()

add_data = ("INSERT INTO esm_data"
               "(StartDate, EndDate, Status, IPAddress, Progress, Duration, Finished, RecordedDate, ResponseId, RecipientLastName,RecipientFirstName, RecipientEmail,ExternalReference, LocationLatitude, LocationLongitude, DistributionChannel, UserLanguage, Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9,Q10,Q11,Q12,Q13,Q14,Q15,Q16,Q17,Q18,app,title,text,created_at,user,time,test,Q5Topics,textTopics) "
               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
add_data2 = ("INSERT INTO esm_data"
               "(StartDate, EndDate) "
               "VALUES (%s,%s)")

filename = 'input.csv'
count = 0
with open(filename, 'r') as f:
    reader = csv.reader(f)
    try:
        for row in reader:
            if(count<3):
                count = count + 1
                continue
            data=(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22],row[23],row[24],row[25],row[26],row[27],row[28],row[29],row[30],row[31],row[32],row[33],row[34],row[35],html.unescape(row[36]),html.unescape(row[37]),row[38],row[39],row[40],row[41],row[42],row[43])
            """
            data = {
            'StartDate': row[0],
            'EndDate': row[1],
            'Status': row[2],
            'IPAddress': row[3],
            'Progress': row[4],
            'Duration': row[5],
            'Finished': row[6],
            'RecordedDate': row[7],
            'ResponseId': row[8],
            -'RecipientLastName': row[9],
            -'RecipientFirstName': row[10],
            -'RecipientEmail': row[11],
            -'ExternalReference' : row[12],
            'LocationLatitude': row[13],
            'LocationLongitude' : row[14],
            -'DistributionChannel' : row[15],
            -'UserLanguage' : row[16],
            'Q1': row[17],
            'Q2': row[18],
            'Q3': row[19],
            'Q4': row[20],
            'Q5': row[21],
            'Q6': row[22],
            'Q7': row[23],
            'Q8': row[24],
            'Q9': row[25],
            'Q10': row[26],
            'Q11': row[27],
            'Q12': row[28],
            'Q13': row[29],
            'Q14': row[30],
            'Q15': row[31],
            'Q16': row[32],
            'Q17': row[33],
            'Q18': row[34],
            'app': row[35],
            'title': row[36],
            'text': row[37],
            'created_at': row[38],
            'user': row[39],
            'time': row[40],
            -'test': row[41],
            'Q5Topics': row[42],
            'textTopics': row[43]
            }
            StartDate, EndDate, Status, IPAddress, Progress, Duration, Finished, RecordedDate, ResponseId, RecipientLastName,RecipientFirstName, RecipientEmail, ExternalReference,ExternalReference, LocationLatitude, LocationLongitude, DistributionChannel, UserLanguage, Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9,Q10,Q11,Q12,Q13,Q14,Q15,Q16,Q17,Q18,app,title,text,created_at,user,time,test,Q5Topics,textTopics
            """
            #print(html.unescape(row[36]))
            cursor.execute(add_data, data)

    except csv.Error as e:
        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

db.commit()
cursor.close()
# disconnect from server
db.close()
