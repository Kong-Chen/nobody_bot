from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import ImageSendMessage
import os
import uuid
from psycopg2.extensions import adapt, register_adapter
import psycopg2
from datetime import datetime
import mysql.connector
import requests
import re
from datetime import datetime, time, timedelta
#import pytz 


app = Flask(__name__)

# 設置你的 LINE Bot 的 Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])


# 註冊 UUID 型別的適應器
def adapt_uuid(uuid):
    return adapt(str(uuid))
register_adapter(uuid.UUID, adapt_uuid)

#發送line_notify
def send_line_notify(message):
    url = 'https://notify-api.line.me/api/notify'
    token = 'TDlRiyRQOrHPIsN0MSfmkQ8cG1dvyllsz3RlBkXe8sG' #鬧鐘
    headers = {
        'Authorization': 'Bearer ' + token
    }
    data = {
        'message': message
    }
    response = requests.post(url, headers=headers, data=data)
    return response


@app.route("/callback", methods=['GET','POST'])
def callback():
    
    if request.method == 'GET':
        
        #current_time = datetime.now().time()
        # 取得現在的台灣時間
        current_time_taiwan = datetime.now() + timedelta(hours=8)
        current_time = current_time_taiwan.time()
        midnight = time(0, 0)
        eight_am = time(8, 0)

        # 設定台灣時區
        #taipei_timezone = pytz.timezone('Asia/Taipei')



        if midnight <= current_time <= eight_am:
            return "OK"
        else :
            # 建立連接 (修改)
            connection = psycopg2.connect(
                host="dpg-cn09uaev3ddc73c0h73g-a.oregon-postgres.render.com",
                port="5432",
                database="kongdb_r77a",
                user="kong",
                password="CvXiRmnIaTOESIwcUU0aAeuVkOYDOKWG"
            )
            cursor = connection.cursor()

            # 使用 %s 作為占位符，並在 execute 的第二個參數中提供實際參數值
            query = """
                SELECT B.user_name, A.last_pee_time
                FROM user_pee_cron A
                JOIN users B ON A.user_no = B.user_no
                WHERE A.last_pee_time < NOW() AT TIME ZONE 'Asia/Taipei' - INTERVAL '3 hours'
            """
            cursor.execute(query, )
            rows = cursor.fetchall()
            
            for row in rows:
                user_name, last_pee_time = row
                message = ('\n' + f"{user_name},上一次廁所已經是{last_pee_time} !!!!，更新範例為：已經在13:00上廁所")
                response = send_line_notify(message)        
            cursor.close()
            connection.close()
            return "OK"
    

        
    elif request.method == 'POST':
        # 處理 POST 請求的邏輯    
        # 取得 request headers 中的 X-Line-Signature 屬性
        signature = request.headers['X-Line-Signature']
        
        # 取得 request 的 body 內容
        body = request.get_data(as_text=True)
        
        try:
            # 驗證簽章
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)
        
        return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    connection = psycopg2.connect(
            host="dpg-cn09uaev3ddc73c0h73g-a.oregon-postgres.render.com",
            port="5432",
            database="kongdb_r77a",
            user="kong",
            password="CvXiRmnIaTOESIwcUU0aAeuVkOYDOKWG"
        )
    cursor = connection.cursor()

    
    # 收到使用者的訊息
    timestamp = datetime.now()
    user_message = event.message.text
    user_line_id = event.source.user_id
    
    #cursor = connection.cursor()
    #cursor.execute("SELECT member_name FROM member")
    #existing_user = cursor.fetchone()



    if event.source.type == 'user' or event.source.type == 'group' or event.source.type == 'room':
        profile = line_bot_api.get_profile(user_line_id)
        user_nickname = profile.display_name

    try:
        cursor = connection.cursor()
        query = "SELECT user_no FROM users WHERE user_id = %s"
        cursor.execute(query, (user_line_id,))
        user_no = cursor.fetchone()
        if not user_no:
            query = "INSERT INTO users (user_id, user_name) VALUES (%s, %s)"
            data = (user_line_id, user_nickname)  
            cursor.execute(query, data)
            connection.commit()
            query = "SELECT user_no FROM users WHERE user_id = %s"
            cursor.execute(query, (user_line_id,))
            user_no = cursor.fetchone()
            
            query = "INSERT INTO user_pee_cron (user_no,last_pee_time) VALUES (%s, %s)"
            data = (user_no,'1999/01/01 00:00:00.000')  
            cursor.execute(query, data)
            connection.commit()
        
  
        
        if user_message =='Nasa':
            # API 密鑰
            api_key = "74K2SccksUYY9UL8P6FPb7oz3Vn0JFacjP5ZPdPh"

            # API 網址
            url = "https://api.nasa.gov/planetary/apod"

            # API 參數
            params = {
                "api_key": api_key
            }

            # 發送 API 請求
            response = requests.get(url, params=params)

            # 取得 API 的返回值
            data = response.json()

            # 顯示照片的網址
            print("Picture URL:", data["url"])
            line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url=data["url"],
                preview_image_url=data["url"]
            )
            )
            
        elif re.match(r'已經在\d{2}:\d{2}上廁所', user_message):
            # user_message = '已經在15:45上廁所'
            # 檢查是否符合格式
                # 使用正規表達式匹配時間格式
            pattern = r'已經在(\d{2}:\d{2})上廁所'
            match = re.match(pattern, user_message)

            if match:
                time_value = match.group(1)
                
                try:
                    datetime.strptime(time_value, '%H:%M')
                    current_date = datetime.now().strftime('%Y-%m-%d')
                    combined_datetime_str = f'{current_date} {time_value}'
                    combined_datetime = datetime.strptime(combined_datetime_str, '%Y-%m-%d %H:%M')                   
                    
                    query = "UPDATE user_pee_cron SET last_pee_time = %s WHERE user_no = %s"
                    data = (combined_datetime, user_no)  
                    cursor.execute(query, data)
                    connection.commit()
                    
                    aaa = (f'收到喔!更新時間為：{combined_datetime}')
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=aaa)
                    )
                except ValueError:
                    aaa = ('未匹配到合法的24小時制時間')
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=aaa)
                    )                
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='不要亂打')
            )
        
    except psycopg2.Error as e:
        # print("資料庫錯誤:", e)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="資料庫錯誤啦!")
        )


    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    # 在本地運行時才啟動伺服器
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))