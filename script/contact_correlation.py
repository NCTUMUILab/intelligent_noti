import MySQLdb
import csv, sys
import html
import secrete as secrete
from scipy import stats

db = MySQLdb.connect(secrete.db_url,secrete.user_name,secrete.password,secrete.db)
cursor = db.cursor()

IOS_list = []
URCS_list = []


cursor.execute("SELECT * FROM contact")  #26:IOS #27~38: URCS
contact_list = cursor.fetchall()

for contact in contact_list:
    IOS = int(contact[26])
    URCS = 0
    for i in range(27,39):
        URCS += float(contact[i])
    URCS /= 12
    IOS_list.append(IOS)
    URCS_list.append(URCS)

print("IOS vs URCS: ",stats.pearsonr(IOS_list, URCS_list))
