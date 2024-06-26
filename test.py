import requests
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

# API密钥和URL
authorization = 'CWA-5AB2578A-4D37-4042-9FBB-777EAAED3040'
url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061"

# 发出请求
response = requests.get(url, {"Authorization": authorization})
response.raise_for_status()  # 检查响应状态码是否为200
resJson = response.json()

# 打印响应数据以调试
# logging.info(f"Response JSON: {resJson}")

# 检查响应数据结构
if "records" in resJson and "locations" in resJson["records"]:
    locations = resJson["records"]["locations"][0]["location"]
else:
    print("响应数据结构不正确")
    exit()

# 定义目标地区和日期
target_district = "士林區"
target_date = "2024-06-29"
target_time = target_date +" 09:00:00"
pop_time = target_date +" 06:00:00" 

for location in locations:
    if location["locationName"] == target_district:
        print(location["locationName"])
        weatherElements = location["weatherElement"]
        for weatherElement in weatherElements:
            if weatherElement["elementName"] == "T":
                timeDicts = weatherElement["time"]
                for timeDict in timeDicts:
                    if timeDict["dataTime"] == target_time:
                        print (target_date+":")
                        print("溫度攝氏:"+timeDict["elementValue"][0]["value"]+"度")
            elif weatherElement["elementName"] == "PoP6h":
                popDicts = weatherElement["time"]
                for popDict in popDicts:
                    if popDict["startTime"] == pop_time:
                        print("降雨機率:"+popDict["elementValue"][0]["value"]+"%")
            elif weatherElement["elementName"] == "WS":
                windDicts = weatherElement["time"]
                for windDict in windDicts:
                    if windDict["dataTime"] == target_time:
                        print("最大風速:"+windDict["elementValue"][0]["value"]+"公尺/秒")
                        
            
            
