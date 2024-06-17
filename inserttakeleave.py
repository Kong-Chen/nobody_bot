import json
import os

def add_takeleave_to_json(lineid, takeleaveday, filename='takeleave.json'):
    takeleave_data = {"lineid": lineid, "takeleaveday": takeleaveday}
    
    # 如果文件存在，檢查文件是否為空
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r') as file:
            data = json.load(file)
    else:
        data = []

    # 檢查用戶是否已經存在，根據lineid和takeleaveday
    for entry in data:
        if entry['lineid'] == lineid and entry['takeleaveday'] == takeleaveday:
            # 如果已經存在，則返回
            return 0

    # 添加新請假數據
    data.append(takeleave_data)

    # 將更新後的數據寫回文件
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    
    return 1

# 範例調用函式，並新增請假記錄
#print (add_takeleave_to_json("U1234567890", "2024-07-15"))
#print (add_takeleave_to_json("U1234567890", "2024-07-16"))
#print (add_takeleave_to_json("U0987654321", "2024-07-15"))
