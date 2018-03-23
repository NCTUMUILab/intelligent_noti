import MySQLdb
import csv, sys
import html

def ESM_amount(ele):
    return int(ele[4])

contact_list = []

db = MySQLdb.connect("ec2-18-220-229-235.us-east-2.compute.amazonaws.com","root","whomatter","who_matter2" )
cursor = db.cursor()

mobileID = sys.argv[1]
#mobileID = "869124021392335"

sql = "SELECT * FROM esm_data WHERE user =" + mobileID
print(sql)


cursor.execute(sql)
results = cursor.fetchall()
with open(mobileID+".csv", 'w', newline='') as f:
    writer = csv.writer(f)
    title = [["time","app","傳送者","內容","你有沒有在手機上感受或注意到通知來的瞬間","你如何感知到這則通知(複選)","在感受到通知的當下，你有沒有猜是誰傳的訊息？","請問你是否有猜對?","請問你剛剛猜的是誰？(請填你猜的人在通訊軟體上的名稱)","你是不是因為你所猜的那個人，而決定看不看這則通知？","你覺得這則通知的干擾程度(1:完全沒干擾；5:非常干擾)","你覺得這個時機點送這則通知如何","你有沒有立即去看這則通知？","這則訊息你預計什麼時候回覆？","這個通知的內容","這個通知的時效性(有急迫性)","你們的關係最可以用下列何者圖示表示","你當時正在做什麼事？","你當時正在做什麼事？-其他","你當時做這件事的專注(投入)程度？(1:非常不投入；5: 非常投入)","你當下在你身邊互動的有多少人？(不包含傳訊息、打電話等等)","你當下在你身邊互動的有誰？(選擇所有符合的身份)","你當下在你身邊互動的有誰?(選擇所有符合的身份)-其他"]]
    writer.writerows(title)
    for row in results:
        time = row[42]
        app = row[37]
        contact_name = row[38]
        text = row[39]
        Q1 = row[18]
        Q2 = row[19]
        Q3 =row[20]
        Q4 =row[21]
        Q5 =row[22]
        Q6 =row[23]
        Q7 =row[24]
        Q8 =row[25]
        Q9 =row[26]
        Q10 =row[27]
        Q11 = row[28]
        Q12 = row[29]
        Q13 =row[30]
        Q14 =row[31]
        Q15 =row[32]
        Q15_other=row[33]
        Q16 =row[34]
        Q17 =row[35]
        Q17_other =row[36]
        #print(text)
        in_list = False

        """
        contact = ["name",interruptibility, respond, percept_count, total ESM, 立即回覆, 在數分鐘之內,在半小時以內,一小時以內,隔數小時之後，但會在當天回覆,不會在當天回覆,不會回覆,沒有預計,closeness]

        """

        data = [[time,app,contact_name,text,Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9,Q10,Q11,Q12,Q13,Q14,Q15,Q15_other,Q16,Q17,Q17_other]]
        writer.writerows(data)
        if(Q1 == "沒有，但已經在其他裝置上看到內容"):
            continue
        for contact in contact_list:
            if(contact_name == contact[0]):
                #print("exist contact: ",contact_name)
                if(Q7 != ''):
                    contact[1] += int(Q7)
                    contact[3] += 1
                contact[4] +=1
                contact[13] += int(Q13)
                if(Q10=="立即回覆"):
                    contact[5]+=1
                elif(Q10=="在數分鐘之內"):
                    contact[6]+=1
                elif(Q10=="在半小時以內"):
                    contact[7]+=1
                elif(Q10=="一小時以內"):
                    contact[8]+=1
                elif(Q10=="隔數小時之後，但會在當天回覆"):
                    contact[9]+=1
                elif(Q10=="不會在當天回覆"):
                    contact[10]+=1
                elif(Q10=="不會回覆"):
                    contact[11]+=1
                elif(Q10=="沒有預計"):
                    contact[12]+=1

                in_list = True
        if(in_list == False):
            #print("add contact: ",contact_name)
            data = [contact_name,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            if(Q7 != ''):
                data[1] += int(Q7)
                data[3] += 1
            data[4] += 1
            data[13] += int(Q13)
            if(Q10=="立即回覆"):
                data[5]+=1
            elif(Q10=="在數分鐘之內"):
                data[6]+=1
            elif(Q10=="在半小時以內"):
                data[7]+=1
            elif(Q10=="一小時以內"):
                data[8]+=1
            elif(Q10=="隔數小時之後，但會在當天回覆"):
                data[9]+=1
            elif(Q10=="不會在當天回覆"):
                data[10]+=1
            elif(Q10=="不會回覆"):
                data[11]+=1
            elif(Q10=="沒有預計"):
                data[12]+=1
                #print(data)
            contact_list.append(data)


    blank = [[]]
    writer.writerows(blank)
    writer.writerows(blank)
    writer.writerows(blank)

    result = [["name","Closeness","Interruptibility", "感知到通知的次數", "total ESM", "立即回覆", "在數分鐘之內","在半小時以內","一小時以內","隔數小時之後，但會在當天回覆","不會在當天回覆","不會回覆","沒有預計"]]
    writer.writerows(result)

    contact_list.sort(reverse=True, key=ESM_amount)
    for contact in contact_list:
        if(float(contact[3]) != 0):
            avg_intr = str(float(contact[1])/float(contact[3]))
        else:
            avg_intr = "no data"
        avg_closeness = str(float(contact[13])/float(contact[4]))
        contact_5 = str(contact[5])+" ("+str(float(contact[5])/float(contact[4])*100)+"%)"
        contact_6 = str(contact[6])+" ("+str(float(contact[6])/float(contact[4])*100)+"%)"
        contact_7 = str(contact[7])+" ("+str(float(contact[7])/float(contact[4])*100)+"%)"
        contact_8 = str(contact[8])+" ("+str(float(contact[8])/float(contact[4])*100)+"%)"
        contact_9 = str(contact[9])+" ("+str(float(contact[9])/float(contact[4])*100)+"%)"
        contact_10 = str(contact[10])+" ("+str(float(contact[10])/float(contact[4])*100)+"%)"
        contact_11 = str(contact[11])+" ("+str(float(contact[11])/float(contact[4])*100)+"%)"
        contact_12 = str(contact[12])+" ("+str(float(contact[12])/float(contact[4])*100)+"%)"

        result_data = [[contact[0],avg_closeness,avg_intr,contact[3],contact[4],contact_5,contact_6,contact_7,contact_8,contact_9,contact_10,contact_11,contact_12]]
        writer.writerows(result_data)

db.close()
