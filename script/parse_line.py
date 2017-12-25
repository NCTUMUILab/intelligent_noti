import os
from datetime import datetime, timedelta
import json
dir_path = os.path.dirname(os.path.realpath(__file__))

files = os.listdir(dir_path)

output = []

fw = open('output.txt', 'w')

for i in files:
    if i[0:6] != '[LINE]':
        continue
    with open(i, 'r') as f:
        lines = f.readlines()
    user_data = {
        'app': 'line',
        'msg_count': 0,
        'day_count': 0,
        'user_name': lines[0].replace('\ufeff[LINE] 與', '').replace('的聊天記錄\n', '')
    }
    time_threshold = datetime.now() - timedelta(days=30)
    time = datetime.now()
    for line in lines:
        try:
            d = datetime.strptime(line[0:10], '%Y/%m/%d')
            time = d
            user_data['day_count']+=1
        except ValueError:
            pass
        # if line[0:2] == '上午' or line[0:2] == '下午':
        if ':' in line and time > time_threshold:
            print(time, "  :    " , time_threshold)
            user_data['msg_count']+=1
    user_data['msg_count'] -= 1
    output.append(user_data)

fw.write(json.dumps(output, ensure_ascii=False))
fw.close()
