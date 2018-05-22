import MySQLdb
import csv, sys
import html
import requests
import secrete as secrete
import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))
from app.helpers.valid_notification import valid_notification

def ESM_amount(ele):
    return int(ele[4])

def Noti_amount(ele):
    return ele["count"]

contact_list = []
notification_list = []

db = MySQLdb.connect(secrete.db_url,secrete.user_name,secrete.password,secrete.db)


cursor = db.cursor()

mobileID = sys.argv[1]
#mobileID = "869124021392335"

cursor.execute("SELECT user_id FROM deviceID WHERE device_id ="+mobileID)
uid = str(cursor.fetchall()[0][0])
print("User id: ",uid)

cursor.execute("SELECT name,Q4,Q9,Q2_1,Q3 FROM contact WHERE uid ="+uid) #Q4: relationship, Q9: closeness, Q2_1: interruptibility, Q3: response,
contact_questionniare= cursor.fetchall()

cursor.execute("SELECT * FROM notification WHERE device_id  ="+mobileID)
notifications = cursor.fetchall()

for noti in notifications:
    if(valid_notification(noti[7],noti[11],noti[8],noti[10],noti[9]) == False):
        #print(noti)
        continue
    contained_in_list = False
    for contact_noti in notification_list:
        if(noti[8] == contact_noti["name"]):
            contact_noti["count"] += 1
            contained_in_list = True
            break
    if(contained_in_list == False):
        data = {"name":noti[8],"count":1,"selected": False}
        notification_list.append(data)

sql = "SELECT * FROM esm_data WHERE user = " + mobileID

cursor.execute(sql)
results = cursor.fetchall()
with open(mobileID+".csv", 'w', newline='') as f:
    writer = csv.writer(f)
    title = [["time","app","傳送者","內容","你有沒有在手機上感受或注意到通知來的瞬間","你如何感知到這則通知(複選)","在感受到通知的當下，你有沒有猜是誰傳的訊息？","請問你是否有猜對?","請問你剛剛猜的是誰？(請填你猜的人在通訊軟體上的名稱)","你是不是因為你所猜的那個人，而決定看不看這則通知？","你覺得這則通知的干擾程度(1:完全沒干擾；5:非常干擾)","你覺得這個時機點送這則通知如何","你有沒有立即去看這則通知？","這則訊息你預計什麼時候回覆？","這個通知的內容","這個通知的時效性(有急迫性)","你們的關係最可以用下列何者圖示表示","你當時正在做什麼事？","你當時正在做什麼事？-其他","你當時做這件事的專注(投入)程度？(1:非常不投入；5: 非常投入)","你當下在你身邊互動的有多少人？(不包含傳訊息、打電話等等)","你當下在你身邊互動的有誰？(選擇所有符合的身份)","你當下在你身邊互動的有誰?(選擇所有符合的身份)-其他"]]
    writer.writerows(title)
    for row in results:
        if(row[7] == "False"):
            continue
        time = row[44]
        app = row[39]
        contact_name = row[40]
        text = row[41]
        Q1 = row[18]
        Q2 = row[19]
        Q2_2 = row[27]
        Q2_2_other = row[28]
        Q3 =row[20]
        Q4 =row[21]
        Q5 =row[22]
        Q6 =row[23]
        Q7 =row[24]
        Q8 =row[25]
        Q9 =row[26]
        Q10 =row[29]
        Q11 = row[30]
        Q12 = row[31]
        Q13 =row[32]
        Q14 =row[33]
        Q15 =row[34]
        Q15_other=row[35]
        Q16 =row[36]
        Q17 =row[37]
        Q17_other =row[38]
        in_list = False

        """
        contact = ["name",interruptibility, respond, percept_count, total ESM, 立即回覆, 在數分鐘之內,在半小時以內,一小時以內,隔數小時之後，但會在當天回覆,不會在當天回覆,不會回覆,沒有預計,closeness, importance, urgence]

        """

        data = [[time,app,contact_name,text,Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9,Q10,Q11,Q12,Q13,Q14,Q15,Q15_other,Q16,Q17,Q17_other]]
        writer.writerows(data)


        if(Q10 == ""):
            #print(Q1)
            continue
        """
        if(Q1 == "沒有，但已經在其他裝置上看到內容"):
            continue
        """
        for contact in contact_list:
            if(contact_name == contact[0]):
                #print("exist contact: ",contact_name)
                if(Q7 != ''):
                    contact[1] += int(Q7)
                    contact[3] += 1
                contact[4] +=1
                contact[13] += int(Q13) #closeness
                if(Q11 == "沒看到沒有任何影響"):
                    contact[14] += 1 #importance
                elif(Q11 == "沒看到不會有太大影響"):
                    contact[14] += 2
                elif(Q11 == "沒看到會有影響"):
                    contact[14] += 3
                elif(Q11 == "沒看到會有明顯的影響"):
                    contact[14] += 4
                elif(Q11 == "非常重要，一定要看到的訊息"):
                    contact[14] += 5

                if(Q12 == "無論什麼時候看到都可以"):
                    contact[15] += 1 #urgence
                elif(Q12 == "當下沒看到不會有太大的影響"):
                    contact[15] += 2
                elif(Q12 == "如果當下沒有看到，會有一點的影響"):
                    contact[15] += 3
                elif(Q12 == "如果當下沒有看到，會有明顯的影響"):
                    contact[15] += 4
                elif(Q12 == "一定當下看到，完全不能延遲"):
                    contact[15] += 5

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
            data = [contact_name,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            if(Q7 != ''):
                data[1] += int(Q7)
                data[3] += 1
            data[4] += 1
            data[13] += int(Q13)
            if(Q11 == "沒看到沒有任何影響"):
                data[14] += 1 #importance
            elif(Q11 == "沒看到不會有太大影響"):
                data[14] += 2
            elif(Q11 == "沒看到會有影響"):
                data[14] += 3
            elif(Q11 == "沒看到會有明顯的影響"):
                data[14] += 4
            elif(Q11 == "非常重要，一定要看到的訊息"):
                data[14] += 5

            if(Q12 == "無論什麼時候看到都可以"):
                data[15] += 1
            elif(Q12 == "當下沒看到不會有太大的影響"):
                data[15] += 2
            elif(Q12 == "如果當下沒有看到，會有一點的影響"):
                data[15] += 3
            elif(Q12 == "如果當下沒有看到，會有明顯的影響"):
                data[15] += 4
            elif(Q12 == "一定當下看到，完全不能延遲"):
                data[15] += 5

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

    final_self_closeness = 0
    final_self_response = 0
    final_self_inter = 0
    questionniare_count = 0
    answered_questionniare = 0

    final_closeness = 0
    final_inter = 0
    final_resp = 0
    final_percept = 0
    final_ESM_count = 0
    final_contact_5 = 0
    final_contact_6 = 0
    final_contact_7 = 0
    final_contact_8 = 0
    final_contact_9 = 0
    final_contact_10 = 0
    final_contact_11 = 0
    final_contact_12 = 0
    final_motivation_count = 0

    final_importance = 0
    final_urgence = 0
    final_notification_count = 0


    result = [["name","notification 總量","關係","自評 Closeness","自評 Interruptibility","自評 回覆動機","Closeness","Interruptibility","回覆動機","重要程度","緊急程度", "total ESM", "立即回覆", "在數分鐘之內","在半小時以內","一小時以內","隔數小時之後，但會在當天回覆","不會在當天回覆","不會回覆","沒有預計"]]
    writer.writerows(result)

    #contact = ["name",interruptibility, respond, percept_count, total ESM, 立即回覆, 在數分鐘之內,在半小時以內,一小時以內,隔數小時之後，但會在當天回覆,不會在當天回覆,不會回覆,沒有預計,closeness, importance, urgence]

    contact_list.sort(reverse=True, key=ESM_amount)
    for contact in contact_list:
        if(float(contact[3]) != 0):
            avg_intr = str(float(contact[1])/float(contact[3]))
            final_closeness += float(contact[13])
            final_percept += float(contact[3])
        else:
            avg_intr = "no data"
        avg_closeness = str(float(contact[13])/float(contact[4]))
        motivation_sum = contact[5]+ contact[6]+contact[7]+contact[8]+contact[9]+contact[10]+contact[11]
        contact_5 = str(contact[5])+" ("+str(float(contact[5])/float(contact[4])*100)+"%)"
        contact_6 = str(contact[6])+" ("+str(float(contact[6])/float(contact[4])*100)+"%)"
        contact_7 = str(contact[7])+" ("+str(float(contact[7])/float(contact[4])*100)+"%)"
        contact_8 = str(contact[8])+" ("+str(float(contact[8])/float(contact[4])*100)+"%)"
        contact_9 = str(contact[9])+" ("+str(float(contact[9])/float(contact[4])*100)+"%)"
        contact_10 = str(contact[10])+" ("+str(float(contact[10])/float(contact[4])*100)+"%)"
        contact_11 = str(contact[11])+" ("+str(float(contact[11])/float(contact[4])*100)+"%)"
        contact_12 = str(contact[12])+" ("+str(float(contact[12])/float(contact[4])*100)+"%)"

        avg_importance = float(contact[14])/float(contact[4])
        avg_urgence = float(contact[15])/float(contact[4])


        if(motivation_sum == 0):
            response_motivation = "no data"
        else:
            response_motivation = str(7 * float(contact[5])/float(motivation_sum) + 6 * float(contact[6])/float(motivation_sum) + 5 * float(contact[7])/float(motivation_sum) + 4 * float(contact[8])/float(motivation_sum) + 3 * float(contact[9])/float(motivation_sum) + 2 * float(contact[10])/float(motivation_sum) + 1 * float(contact[11])/float(motivation_sum))
            final_resp += 7 * float(contact[5]) + 6 * float(contact[6])+ 5 * float(contact[7])+ 4 * float(contact[8]) + 3 * float(contact[9])+ 2 * float(contact[10]) + 1 * float(contact[11])
            final_motivation_count += motivation_sum

        final_inter += float(contact[1])
        final_ESM_count += float(contact[4])
        final_contact_5 += int(contact[5])
        final_contact_6 += int(contact[6])
        final_contact_7 += int(contact[7])
        final_contact_8 += int(contact[8])
        final_contact_9 += int(contact[9])
        final_contact_10 += int(contact[10])
        final_contact_11 += int(contact[11])
        final_contact_12 += int(contact[12])

        final_importance += int(contact[14])
        final_urgence += int(contact[15])

        relationship = ""
        self_closeness = ""
        self_interr = ""
        self_response = ""
        noti_count = 0
        for questionniare in contact_questionniare:
            if(questionniare[0] == contact[0]):
                relationship = questionniare[1]
                self_closeness = questionniare[2]
                self_interr = questionniare[3]
                self_response = questionniare[4]
                final_self_inter += float(questionniare[3])

                if(self_response=="通常立即回覆"):
                    final_self_response += 7
                elif(self_response=="通常間隔數分鐘"):
                    final_self_response += 6
                elif(self_response=="通常半小時以內"):
                    final_self_response += 5
                elif(self_response=="通常一小時以內"):
                    final_self_response += 4
                elif(self_response=="通常幾小時內（當天）"):
                    final_self_response += 3
                elif(self_response=="通常沒有在當天回覆"):
                    final_self_response += 2
                elif(self_response=="通常不回覆"):
                    final_self_response += 1
                final_self_closeness += float(questionniare[2])
                questionniare_count += 1
        print(contact[0])
        for data in notification_list:
            if (data["name"] == contact[0]):
                data["selected"] = True
                noti_count = data["count"]
                break

        final_notification_count += noti_count
        result_data = [[contact[0],noti_count,relationship,self_closeness,self_interr,self_response,avg_closeness,avg_intr,response_motivation,avg_importance,avg_urgence, contact[4],contact_5,contact_6,contact_7,contact_8,contact_9,contact_10,contact_11,contact_12]]
        writer.writerows(result_data)

    notification_list.sort(reverse=True, key=Noti_amount)
    for data in notification_list:
        if (data["selected"] == False):
            print(data["name"])
            final_notification_count += data["count"]
            writer.writerows([[data["name"],data["count"]]])

    print("questionnarie conact: ",str(questionniare_count))
    if(questionniare_count==0):
        questionniare_count = 1
    final_data = [["Total",final_notification_count,"",final_self_closeness/questionniare_count,float(final_self_inter)/questionniare_count,float(final_self_response)/questionniare_count,final_closeness/final_ESM_count,final_inter/final_percept,final_resp/final_motivation_count,float(final_importance)/final_ESM_count,float(final_urgence)/final_ESM_count,int(final_ESM_count), str(final_contact_5)+" ("+str(float(final_contact_5)/float(final_ESM_count)*100)+"%)",str(final_contact_6)+" ("+str(float(final_contact_6)/float(final_ESM_count)*100)+"%)",str(final_contact_7)+" ("+str(float(final_contact_7)/float(final_ESM_count)*100)+"%)",str(final_contact_8)+" ("+str(float(final_contact_8)/float(final_ESM_count)*100)+"%)",str(final_contact_9)+" ("+str(float(final_contact_9)/float(final_ESM_count)*100)+"%)",str(final_contact_10)+" ("+str(float(final_contact_10)/float(final_ESM_count)*100)+"%)",str(final_contact_11)+" ("+str(float(final_contact_11)/float(final_ESM_count)*100)+"%)",str(final_contact_12)+" ("+str(float(final_contact_12)/float(final_ESM_count)*100)+"%)" ]]
    writer.writerows(final_data)


db.close()
