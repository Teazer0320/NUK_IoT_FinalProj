from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction
import json
from pprint import pprint
from linebot.exceptions import InvalidSignatureError
from linebot import LineBotApi, WebhookHandler
from flask import request, abort, jsonify
from flask import Flask, render_template, url_for, redirect
app = Flask(__name__)
import pymysql
from io import BytesIO
import cv2
import numpy as np
import base64
import datetime
import socket

# LINE 聊天機器人的基本資料
LINE_CHANNEL_ACCESS_TOKEN = "Pa7wrVG1lVy5pWueyME62YrPVl0eE5p7ujp0k3oWqA3+i9NObjUWPXB0tGaXirZsjlth8RCG92xKpDmR6i2mtcA26Yx43XlTPc3tbS5+4ASSvqTDI3lvBIbyB0MvwTTupxC+0VLiAa6mnNU4ClFDjgdB04t89/1O/w1cDnyilFU="

LINE_CHANNEL_SECRET = "9059a5516e98f71f5462bc4ded873918"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

imgshape = (480, 640, 3)

def planttype2img(plant_type):
    # [TODO] Complete the mapping
    mapping = {
        "沙漠玫瑰": "img/desert_rose_icon.png",
        "薄荷": "img/mint_icon.png"
    }
    return mapping[plant_type] if plant_type in mapping else None

# 接收 LINE 的資訊

def query_pic_fromDB(plant_id):
    
    cursor = db.cursor()
    cursor.execute("select * from plant_picture where plant_id=%s;", plant_id)
    
    pics = cursor.fetchall()

    ret_pics = []
    for pic in pics:
        # img = base64.b64encode(pic[3]).decode("utf-8")
        img = np.frombuffer(pic[3], dtype=np.uint8).reshape(imgshape)
        _, img = cv2.imencode(".jpg", img)
        img = base64.b64encode(img).decode("utf-8")

        ret_pics.append({
            "date": pic[2],
            "img": img})

    cursor.close()
    
    return ret_pics

def query_plant_fromDB(user_id):
    cursor = db.cursor()
    cursor.execute("select plant_id,plant_name,plant_type from plant where user_id=%s;", user_id)
    plants = cursor.fetchall()

    ret_plants = []
    for plant in plants:
        ret_plants.append({
            'id': plant[0],
            'name': plant[1],
            'plant_type': plant[2],
        })
    cursor.close()
    
    return ret_plants

def query_record_fromDB(plant_id, date):
    cursor = db.cursor()
    cursor.execute("select * from env_control_record where (plant_id = {}) and (control_time like '{}%');".format(plant_id, date))
    records = cursor.fetchall()

    ret_records = []
    for record in records:
        ret_records.append({
            "control_time": record[1],
            "humidity": record[3]
        })
    cursor.close()

    return ret_records

def query_envdata_fromDB(plant_id):
    cursor = db.cursor()
    cursor.execute("select humidity from current_env where plant_id = %s;", plant_id)
    envdatas = cursor.fetchall()
    for envdata in envdatas:
        ret_envdata = {
            "humidity": envdata[0]
        }
    cursor.close()
    print(ret_envdata)

    return ret_envdata

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
    data = query_plant_fromDB(0)
    return render_template("Home.html", data=data)

@app.route("/plant/<plant_id>")
def plant_page(plant_id):
    envdata = query_envdata_fromDB(plant_id)
    return render_template("FunctionList.html", plant_id=plant_id, envdata=envdata)

@app.route("/control_record/<plant_id>")
def envcontrol_record(plant_id):
    # return 'Plant' + plant_id
    date = request.args.get('querydate', datetime.date.today())
    records = query_record_fromDB(plant_id, date)
    return render_template("EnvControlRecord.html", date=date, records=records)

@app.route("/plant/watch/<plant_id>")
def watch_plant(plant_id):
    # return 'Plant' + plant_id
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 8888))
    sock.send(b"rt")
    sock.recv(64)
    img = cv2.imread("rtimg.jpg")
    img = img.tobytes()
    img = np.frombuffer(img, dtype=np.uint8).reshape(imgshape)
    _, img = cv2.imencode(".jpg", img)
    img = base64.b64encode(img).decode("utf-8")
    return render_template("WatchPlant.html", plant_id=plant_id, img=img)

@app.route("/plant/diary/<plant_id>")
def plant_diary(plant_id):
    # return 'Plant' + plant_id
    pics_data = query_pic_fromDB(plant_id)
    return render_template("PlantDiary.html", pics_data=pics_data, plant_id=plant_id)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    mtext = event.message.text
    try:
        message = TextSendMessage(text=mtext)
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='發生錯誤！'))


@app.route("/plant/recognize", methods=["GET"])
def recognize_plant():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 8888))
    sock.send(b"recognize")
    label = sock.recv(64).decode("utf-8")
    img = cv2.imread("rtimg.jpg")
    img = img.tobytes()
    img = np.frombuffer(img, dtype=np.uint8).reshape(imgshape)
    _, img = cv2.imencode(".jpg", img)
    img = base64.b64encode(img).decode("utf-8")
    print("label", label)
    return jsonify({"label": label, "img": img})

@app.route("/plant/confirmcreate", methods=["POST"])
def create_plant_toDB():
    cursor = db.cursor()
    p_type =  int(request.values["plant_type"])
    plant_type = ["沙漠玫瑰", "薄荷", "溫達骨葵", "烏羽玉"][p_type]

    new_plant = {
        "user_id": 0,
        "plant_name": request.values["plant_name"],
        "plant_type": plant_type,
        "machine_id": request.values["machine_id"]   
    }

    insert_sql = "insert into `plant`(`user_id`,`plant_name`,`plant_type`,`machine_id`) values (%s,%s,%s,%s);"

    cursor.execute(insert_sql, tuple([v for k, v in new_plant.items()]))
    db.commit()
    cursor.execute("select LAST_INSERT_ID();")
    result = cursor.fetchone()
    plant_id=result[0]
    return redirect(url_for('plant_page',plant_id=plant_id))

@app.route("/plant/create", methods=["GET", "POST"])
def create_plant():
    return render_template("CreatePlant.html")

if __name__ == '__main__':
    db_settings = {
        "host": "127.0.0.1",
        "user": "elf",
        "password": "elfgroup4",
        "database": "elfdb",
    }
    global db 
    db = pymysql.connect(**db_settings)

    # Register global function to template
    app.jinja_env.globals.update(planttype2img=planttype2img)
    app.run(port=8000, debug=True)
    db.close()
