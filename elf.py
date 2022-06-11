from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction
import json
from pprint import pprint
from linebot.exceptions import InvalidSignatureError
from linebot import LineBotApi, WebhookHandler
from flask import request, abort
from flask import Flask, render_template
app = Flask(__name__)


# LINE 聊天機器人的基本資料
LINE_CHANNEL_ACCESS_TOKEN = "Pa7wrVG1lVy5pWueyME62YrPVl0eE5p7ujp0k3oWqA3+i9NObjUWPXB0tGaXirZsjlth8RCG92xKpDmR6i2mtcA26Yx43XlTPc3tbS5+4ASSvqTDI3lvBIbyB0MvwTTupxC+0VLiAa6mnNU4ClFDjgdB04t89/1O/w1cDnyilFU="

LINE_CHANNEL_SECRET = "9059a5516e98f71f5462bc4ded873918"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 接收 LINE 的資訊


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

@app.route("/")
def homepage():
	return render_template("Home.html")

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    mtext = event.message.text
    try:
        message = TextSendMessage(text=mtext)
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='發生錯誤！'))


if __name__ == '__main__':
    app.run(port=8000)
