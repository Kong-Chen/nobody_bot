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
import psycopg2
import requests
import re
from datetime import datetime, time, timedelta
from checkday import get_weekday_in_taiwan





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
    
    #排程用
    if request.method == 'GET':
        current_time = datetime.utcnow() + timedelta(hours=8)
        year = current_time.year
        month = current_time.month
        day = current_time.day
        date_to_check = datetime(year, month, day)
        
        if get_weekday_in_taiwan(date_to_check) == 4 :
            message = ('\n' + f"請假人有.....")
            response = send_line_notify(message)
        
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
    
    # 建立連接 (修改)
    connection = psycopg2.connect(
        host="dpg-cpp4jouehbks73brha50-a.oregon-postgres.render.com",
        port="5432",
        database="nobody_y10j",
        user="kong",
        password="yydSDvrjnBhY68izhYu7UhRiiQPdPGth"
    )
      
    # 收到使用者的訊息
    user_message = event.message.text
    user_line_id = event.source.user_id

    if event.source.type == 'user' or event.source.type == 'group' or event.source.type == 'room':
        profile = line_bot_api.get_profile(user_line_id)
        user_nickname = profile.display_name

    try:
        # 新增使用者
        cursor = connection.cursor()
        query = """
        INSERT INTO users (user_id, user_name)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO NOTHING;
        """
        cursor.execute(query, (user_line_id, user_nickname))
        connection.commit()
        
        # 對話關鍵字判斷開始 *****************
        if user_message =='功能':
            aaa = (f"1.請假：0520請假"+'\n' + f"2.請假取消：0520請假取消"+'\n' + f"3.請假查詢：0520查詢")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=aaa)
            )
            
        elif re.match(r'\d{4}請假', user_message):
            # 使用正規表達式匹配日期格式
            pattern = r'(\d{2})(\d{2})請假'
            match = re.match(pattern, user_message)

            if match:
                month = match.group(1)
                day = match.group(2)
                year = datetime.now().year
                date_str = f"{year}-{month}-{day}"

                try:
                    if get_weekday_in_taiwan(date_str) > 5 : #如果是假日
                    
                        response_message = f"收到請假"
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=response_message)
                        )

                    else:
                        response_message = f"請假日期非假日!!!!"
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=response_message)
                        )
                        
                except ValueError:
                    warning_message = '日期格式不正確，請檢查輸入。'
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=warning_message)
                    )
            else:
                warning_message = '請輸入正確的日期格式，範例如：0520請假'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=warning_message)
                )
        else: #不能亂講話
            warning_message = '請不要亂打，或輸入(功能)來看提示!!!!'
        
    except psycopg2.Error as e:
        # print("資料庫錯誤:", e)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="資料庫錯誤啦!")
        )

if __name__ == "__main__":
    # 在本地運行時才啟動伺服器
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))