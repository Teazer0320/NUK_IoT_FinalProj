import cv2
from sys import argv, stderr
import os
import threading
import time, requests
import datetime
import numpy as np
from PIL import Image
from tensorflow.keras import models
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import socket
import pymysql
import DAN
from apscheduler.schedulers.blocking import BlockingScheduler

ServerURL = "http://2.iottalk.tw:9999"
Reg_addr = None
DAN.profile["dm_name"] = "Watering"
DAN.profile["df_list"] = ["plant_type", "moisture", "water_control" ]

cap_img = {}
plant_pred = None
moisture_record = [2, 0]
watering_record = [2, 0, 0]

cap = cv2.VideoCapture(0)
# shape: 480, 640, 3
# dtype: uint8

def insert_pic_intoDB(pic):
	db_settings = {
		"host": "127.0.0.1",
		"user": "elf",
		"password": "elfgroup4",
		"database": "elfdb",
	}
	db = pymysql.connect(**db_settings)
	cursor = db.cursor()
	pic_bin = pic.tobytes()
	
	cursor.execute("insert into plant_picture (machine_id, plant_pic, plant_id) values(%s, %s, 2);", ("FF:EE:AA:FF:CC:BB", pic_bin))
	db.commit()
	
	cursor.close()
	db.close()


def insert_moisture_intoDB(data):
	db_settings = {
		"host": "127.0.0.1",
		"user": "elf",
		"password": "elfgroup4",
		"database": "elfdb",
	}
	db = pymysql.connect(**db_settings)
	cursor = db.cursor()
	# modify this
	cursor.execute("UPDATE current_env SET humidity = %s WHERE plant_id = %s ;", (data[1], data[0]))
	db.commit()
	
	cursor.close()
	db.close()


def insert_watering_intoDB(data):
	db_settings = {
		"host": "127.0.0.1",
		"user": "elf",
		"password": "elfgroup4",
		"database": "elfdb",
	}
	db = pymysql.connect(**db_settings)
	cursor = db.cursor()
	
	# modify this
	cursor.execute("insert into env_control_record (plant_id, operation, humidity) values(%s, %s, %s);", (data[0], data[1],data[2]))
	db.commit()
	
	cursor.close()
	db.close()

def run_cap():
	global cap_img, plant_pred
	model = models.load_model("cnn_model.h5")
	while True:
		ret, frame = cap.read()
		if ret:
			cap_img[0] = frame
		 
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			frame.resize((100, 100, 1))
			img = frame
			
			xlist = []
			for i in range(6):
				step = 100 // 6
				xlist.append(img[:, i * step:(i + 1) * step] / 255)
			pred = np.argmax(model.predict(np.array(xlist)), 1)
			label_votes = [0, 0, 0, 0]
			for p in pred:
				label_votes[p // 2] += 1
			plant_pred = label_votes.index(max(label_votes))

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break


	cap.release()

def store_upload_img():
	
	try:
		DAN.push("plant_type", plant_pred)
		insert_pic_intoDB(cap_img[0])
		print("put", plant_pred)
	except Exception as e:
		print(e)

def download_mc2db():
	try:
		ODF_data1 = DAN.pull('moisture') #Pull data from an output device feature "Dummy_Control"
		ODF_data2 = DAN.pull('water_control')
		if ODF_data1 != None and ODF_data2 != None:
		    print('get moistrue:'+str(ODF_data1[0]))   #print (ODF_data[0])
		    print('get water_control'+str(ODF_data2[0]))
		    #傳回資料庫(不管有沒有要澆水)即時資料
		    # 傳濕度(回傳值*100/1024)
		    humidity = (int)((ODF_data1[0] * 100)/1024)
		    moisture_record[1] = humidity
		    print("insert_moisture...")
		    insert_moisture_intoDB(moisture_record)
	
		    print('get plant type...\n')
		    print("start watering...\n")
		    if ODF_data2[0] == 1:
		    #傳回資料庫(有要澆水)照護資料
			    watering_record[1]=0
			    watering_record[2]=humidity
			    insert_watering_intoDB(watering_record)
	except Exception as e:
		print(e)


def runSock():
	global plant_pred
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(("127.0.0.1", 8888))
	sock.listen(8)
	print("run socket...")
	while(True):
		conn, addr = sock.accept()
		msg = conn.recv(1024).decode("utf-8")
		print(msg)
		ret_pred = str(plant_pred).encode("utf-8")
		cv2.imwrite("../rtimg.jpg", cap_img[0])
		print("ret_pred:", ret_pred)
		if msg == "recognize":
			conn.send(bytes(ret_pred))
		else:
			conn.send(b"[OK]")
		conn.close()


def main():
	if len(argv) >= 2:
		DAN.deregister()
		exit()
	DAN.device_registration_with_retry(ServerURL, Reg_addr)
	cap_thread = threading.Thread(target = run_cap)
	cap_thread.start()

	sock_thread = threading.Thread(target = runSock)
	sock_thread.start()

	sched = BlockingScheduler(timezone="Asia/Shanghai")

	sched.add_job(store_upload_img, "interval", seconds=10)
	
	sched.add_job(download_mc2db, "interval", seconds=10)
	sched.start()


	cap_thread.join()
	sock_thread.join()
	cv2.destroyAllWindows()
		

if __name__ == "__main__":
	main()
	
