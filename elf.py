from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction
import json
from pprint import pprint
from linebot.exceptions import InvalidSignatureError
from linebot import LineBotApi, WebhookHandler
from flask import request, abort
from flask import Flask, render_template
app = Flask(__name__)
import pymysql
import cv2
import numpy as np

# LINE 聊天機器人的基本資料
LINE_CHANNEL_ACCESS_TOKEN = "Pa7wrVG1lVy5pWueyME62YrPVl0eE5p7ujp0k3oWqA3+i9NObjUWPXB0tGaXirZsjlth8RCG92xKpDmR6i2mtcA26Yx43XlTPc3tbS5+4ASSvqTDI3lvBIbyB0MvwTTupxC+0VLiAa6mnNU4ClFDjgdB04t89/1O/w1cDnyilFU="

LINE_CHANNEL_SECRET = "9059a5516e98f71f5462bc4ded873918"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 接收 LINE 的資訊

def query_pic_fromDB():
    db_settings = {
        "host": "127.0.0.1",
        "user": "elf",
        "password": "elfgroup4",
        "database": "elf",
    }
    db = pymysql.connect(**db_settings)
    cursor = db.cursor()
    cursor.execute("select * from plant;")
    
    pics = cursor.fetchall()
    
    imgshape = (480, 640, 3)

    ret_pics = []
    for pic in pics:
        img = np.frombuffer(pic[2], dtype=np.uint8)
        img = img.reshape(imgshape)
        ret_pics.append((pic[0], pic[1], img))
    cursor.close()
    db.close()

    return ret_pics

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)  # get request body as text

    try:
        handler.handle(body, signature)
    except InvalidSignatureError as err:
        print("Err: ", err)
        abort(400)
    return 'OK'

<<<<<<< HEAD
=======
@app.route("/")
def homepage():
    return render_template("Home.html")

>>>>>>> 5fde4c49c88d06b4e80994ae7dbddf19bbb53b3d
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    mtext = event.message.text
    try:
        message = TextSendMessage(text=mtext)
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='發生錯誤！'))


@app.route("/")
def homepage():
	return render_template("Home.html")

@app.route("/plant/create", methods=["GET", "POST"])
def createPlant():
    """
    utility:

    """
    return render_template("CreatePlant.html")

if __name__ == '__main__':
    app.run(port=8000)

