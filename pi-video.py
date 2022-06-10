import cv2
from sys import argv, stderr
import os
import threading
import time
import numpy as np
from PIL import Image
from tensorflow.keras import models
from tensorflow.keras.preprocessing.image import load_img, img_to_array

cap_num = [0, 1]
cap_img = {}
model = models.load_model("cnn_model.h5")
lock = threading.Lock()



def run_cap(idx):
	global model, lock
	cap = cv2.VideoCapture(idx)
	print("camera %d open"%(idx))
	while True:
		ret, frame = cap.read()
		if ret:
			cap_img[idx] = frame
			# cv2.imshow("live %d"%(idx), frame)
		 
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			frame.resize((100, 100, 1))
			img = frame
			"""
			xlist = []
			for i in range(6):
				step = 100 // 6
				xlist.append(img[:, i * step:(i + 1) * step] / 255)
			lock.acquire()
			pred = np.argmax(model.predict(np.array(xlist)), 1)
			print(idx, pred)
			lock.release()
			time.sleep(2)
			"""
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break


	cap.release()

def main():
	print(model)
	"""
	if (len(argv) == 2):
		file_name = argv[1]
		img = load_img(file_name, color_mode="grayscale")
		img = img_to_array(img.resize((100, 100)))
		xlist = []
		for i in range(6):
			step = 100 // 6
			xlist.append(img[:, i * step:(i + 1) * step] / 255)
		pred = np.argmax(model.predict(np.array(xlist)), 1)
		print(pred)
		return
	"""

	threads = []
	for i in range(len(cap_num)):
		threads.append(threading.Thread(target = run_cap, args = (cap_num[i],)))
		threads[i].start()

	cap_idx = 0
	i = 0;
	while True:
		if cap_idx in cap_img.keys():
			cv2.imshow("live", cap_img[0])
		i += 1
		if i & 0xFF == 0:
			cap_idx ^= 0 ^ 1
			print(cap_idx)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break


	for i in range(len(cap_num)):
		threads[i].join()

	cv2.destroyAllWindows()
		


if __name__ == "__main__":
	main()
	
