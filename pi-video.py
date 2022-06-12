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

ServerURL = "http://2.iottalk.tw:9999"
Reg_addr = None
DAN.profile["dm_name"] = "Dummy_Device"
DAN.profile["df_list"] = ["Dummy_Sensor", "Dummy_Control", ]



cap_img = {}

def insert_pic_intoDB(pic):
	db_settings = {
		"host": "127.0.0.1",
		"user": "elf",
		"password": "elfgroup4",
		"database": "elf",
	}
	db = pymysql.connect(**db_settings)
	cursor = db.cursor()
	# print(pic.shape)  (480, 640, 3)
	print(pic.dtype)
	pic_bin = pic.tobytes()
	#ts = time.time()
	# timestamp = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
		
	cursor.execute("insert into plant (machine_id, plant_pic) values(%s,%s);", ("FF:EE:AA:FF:CC:BB", pic_bin))
	db.commit()
	record = cursor.fetchall()
	print(record)
	# print(pic_bin)
	
	cursor.close()
	db.close()

def run_cap():
	global cap_img
	model = models.load_model("cnn_model.h5")
	cap = cv2.VideoCapture(0)
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
			pred = label_votes.index(max(label_votes))
			try:
#				DAN.push("Dummy_Sensor", pred)
				print("put", pred)
			except Exception as e:
				print(e)

			# time.sleep(5)
			


		if cv2.waitKey(1) & 0xFF == ord('q'):
			break


	cap.release()

def main():
	if len(argv) >= 2:
		DAN.deregister()
		exit()
#	DAN.device_registration_with_retry(ServerURL, Reg_addr)
	cap_thread = threading.Thread(target = run_cap)
	cap_thread.start()

	cap_idx = 0
	first = False
		
	while True:
		
		if cap_idx in cap_img.keys():
			cv2.imshow("live", cap_img[0])
			if first == False:
				first = True
				insert_pic_intoDB(cap_img[0])
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cap_thread.join()

	cv2.destroyAllWindows()
		


if __name__ == "__main__":
	main()
	
