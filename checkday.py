from datetime import datetime, timedelta

def get_weekday_in_taiwan(date):
    # 轉換成台灣時間
    taiwan_time = date + timedelta(hours=8)
    
    # 取得星期幾 (0 = 星期一, 1 = 星期二, ..., 6 = 星期日)
    weekday = taiwan_time.weekday()
    return weekday+1
