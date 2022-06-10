import cv2
from sys import argv, stderr
import os
import threading
import time
import numpy as np
from PIL import Image
from tensorflow.keras import models
from tensorflow.keras.preprocessing.image import load_img, img_to_array

WORK_NUM = 2
cam_num = [0, 2]

def main():
	global model
	model = models.load_model("cnn_model.h5")
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
	cap = cv2.VideoCapture(0)

	while True:
		ret, frame = cap.read()
		cv2.imshow("live", frame)
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		frame.resize((100, 100, 1))
		img = frame
		
		xlist = []
		for i in range(6):
			step = 100 // 6
			xlist.append(img[:, i * step:(i + 1) * step] / 255)
		pred = np.argmax(model.predict(np.array(xlist)), 1)
		print(pred)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break


	cap.release()
	cv2.destroyAllWindows()
		


if __name__ == "__main__":
	main()
	
