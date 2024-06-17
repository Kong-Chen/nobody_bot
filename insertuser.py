import json
import os

def add_user_to_json(lineid, name, filename='user.json'):
    user_data = {"lineid": lineid, "name": name}
    
    # 如果文件存在，讀取現有數據
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
    else:
        data = []

    # 檢查用戶是否已經存在，根據lineid
    for user in data:
        if user['lineid'] == lineid:
            # print(f"User with lineid {lineid} already exists.")
            return

    # 添加新用戶數據
    data.append(user_data)

    # 將更新後的數據寫回文件
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    
    # print(f"User with lineid {lineid} and name {name} added successfully.")
