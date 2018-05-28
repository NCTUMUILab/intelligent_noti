import MySQLdb
import csv, sys
import html
import secrete as secrete
from scipy import stats

db = MySQLdb.connect(secrete.db_url,secrete.user_name,secrete.password,secrete.db)
cursor = db.cursor()

IOS_list = []
URCS_list = []
Interruptibility_list = []
Depandance_list = []
Mobile_maintainace_list = []
Answering_expectation_list = []
Obligation_to_answer_list = []

Correlation_list = [Interruptibility_list,IOS_list,URCS_list,Depandance_list,Mobile_maintainace_list,Answering_expectation_list,Obligation_to_answer_list]


cursor.execute("SELECT * FROM contact")  #26:IOS    #27~38: URCS       #39~45:depandance      #46~54:mobile mantainace      #55~60: obligation to answer       #61~66: expection to answer
contact_list = cursor.fetchall()

for contact in contact_list:
    depandance = 0
    for i in range(39, 46):
        if(i == 41 or i==45):
            depandance += float((int(contact[i])-6)*(-1))
        else:
            depandance += float(contact[i])

    depandance /= 7

    mobile_maintainace = 0
    for i in range(46,55):
        mobile_maintainace += float(contact[i])

    mobile_maintainace /= 9

    answering_expectation = 0
    for i in range(61,67):
        answering_expectation += float(contact[i])

    answering_expectation /= 6


    obligation_to_answer = 0
    for i in range(55,61):
        obligation_to_answer += float(contact[i])

    obligation_to_answer /= 6

    IOS = int(contact[26])
    URCS = 0
    for i in range(27,39):
        URCS += float(contact[i])
    URCS /= 12

    interruptibility = int(contact[18])
    print(interruptibility)

    Interruptibility_list.append(interruptibility)
    Obligation_to_answer_list.append(obligation_to_answer)
    Answering_expectation_list.append(answering_expectation)
    Mobile_maintainace_list.append(mobile_maintainace)
    Depandance_list.append(depandance)
    IOS_list.append(IOS)
    URCS_list.append(URCS)

print("Interruptibility_list,IOS_list,URCS_list,Depandance_list,Mobile_maintainace_list,Answering_expectation_list,Obligation_to_answer_list")

for a in Correlation_list:
    for b in Correlation_list:
        print("%6.3f(%6.4f)" %(stats.pearsonr(a, b)[0], stats.pearsonr(a, b)[1]), end=" ")
    print("|")

"""
print("IOS vs URCS: ",stats.pearsonr(IOS_list, URCS_list))
print("Interruptibility vs IOS", )
print("Interruptibility vs URCS")
print("depandance vs Interruptibility")
print("mobile mantainace vs Interruptibility")
print("answering expectation vs")
"""
