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
DAN.profile["dm_name"] = "Dummy_Device"
DAN.profile["df_list"] = ["Dummy_Sensor", "Dummy_Control", ]



cap_img = {}
plant_pred = None

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
		DAN.push("Dummy_Sensor", plant_pred)
		# insert_pic_intoDB(cap_img[0])
		print("put", plant_pred)
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
		ret_pred = plant_pred
		cv2.imwrite("rtimg.jpg", cap_img[0])
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
	
	sched.start()


	cap_thread.join()
	sock_thread.join()
	cv2.destroyAllWindows()
		


if __name__ == "__main__":
	main()
	
