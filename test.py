from datetime import datetime, timedelta

# 获取当前UTC时间并转换为台湾时间
current_time = datetime.utcnow() + timedelta(hours=8)

# 获取当前年份、月份和日期
year = current_time.year
month = current_time.month
day = current_time.day
minute = current_time.minute


# 检查是否为星期五和早上8点
print(current_time.weekday())
print(current_time.hour)
print(current_time.minute)

