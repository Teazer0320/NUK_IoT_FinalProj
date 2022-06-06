import numpy as np
import os
from PIL import Image
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import models
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing.image import load_img

#### flowrs #############################
# 0 沙漠玫瑰    Desert Rose             #
# 1 烏羽玉      Lophophora williamsii   #
# 2 薄荷        Mint                    #
# 3 溫達骨葵    Monsonia vanderietiae   #
#########################################

# initialize variables
# trainingSet的路徑
path = 'trainDataset/'
img_foldernames = os.listdir(path)
classname = {'0_withFlower': 0,'0_withoutFlower': 1,'1_withFlower': 2,'1_withoutFlower': 3,'2_withFlower': 4, '2_withoutFlower': 5,'3_withFlower':6,'3_withoutFlower':7}

epochs = 1000  # 訓練的次數
img_rows = 100  # 驗證碼影像檔的高
img_cols = 100  # 驗證碼影像檔的寬
digits_in_img = 6  # 驗證碼影像檔中有幾位數
x_list_train = list()  # 存所有驗證碼數字影像檔的array
y_list_train = list()  # 存所有的驗證碼數字影像檔array代表的正確數字
x_list_test = list()  # 存所有驗證碼數字影像檔的array
y_list_test = list()  # 存所有的驗證碼數字影像檔array代表的正確數字
x_train = list()  # 存訓練用驗證碼數字影像檔的array
y_train = list()  # 存訓練用驗證碼數字影像檔array代表的正確數字
x_test = list()  # 存測試用驗證碼數字影像檔的array
y_test = list()  # 存測試用驗證碼數字影像檔array代表的正確數字
classes_pic_num = list()
# split digits in img


def split_digits_in_img(img_array, x_list, y_list):
    for i in range(digits_in_img):
        step = img_cols // digits_in_img
        x_list.append(img_array[:, i * step:(i + 1) * step] / 255)
        # print(classname[img_foldername])
        y_list.append(classname[img_foldername])

def get_mode(predict_result):
    counts = np.bincount(predict_result)
    mode = np.argmax(counts)
    return mode



for img_foldername in img_foldernames:
    print("fold loading:",img_foldername)
    count=0
    for img_filename in os.listdir(path + img_foldername):
        path_file = path + img_foldername
        #print(img_filename)
        if '.jpg' not in img_filename:
            continue
        img = load_img(
            path_file + '/{0}'.format(img_filename), color_mode='grayscale')
        img_resize = img.resize((100, 100))
        img_array = img_to_array(img_resize)
        img_rows, img_cols, _ = img_array.shape
        # print("rows,cols = ", img_rows, img_cols)
        #取前面30%的影像當作validation
        if(count<int(len(os.listdir(path + img_foldername))*0.3)):
            split_digits_in_img(img_array,x_list_test,y_list_test)
        else:
            split_digits_in_img(img_array,x_list_train,y_list_train)

        count = count+1
    classes_pic_num.append(int((count+1)*0.3))

y_list_train = keras.utils.to_categorical(y_list_train, num_classes=10)
y_list_test = keras.utils.to_categorical(y_list_test, num_classes=10)
x_train = x_list_train
x_test = x_list_test
y_train = y_list_train
y_test = y_list_test

#改成自己的模型路徑
if os.path.isfile('./cnn_model.h5'):
    model = models.load_model('cnn_model.h5')
    print('Model loaded from file.')
else:
    model = models.Sequential()
    model.add(layers.Conv2D(32, kernel_size=(3, 3), activation='relu',
              input_shape=(img_rows, img_cols // digits_in_img, 1)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D(pool_size=(2, 2)))
    model.add(layers.Dropout(rate=0.25))
    model.add(layers.Flatten())
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(rate=0.5))
    model.add(layers.Dense(10, activation='softmax'))
    print('New model created.')
    model.compile(loss=keras.losses.categorical_crossentropy,
                optimizer=keras.optimizers.Adam(), metrics=['accuracy'])
    model.fit(np.array(x_train), np.array(y_train), batch_size=digits_in_img,
            epochs=epochs, verbose=1, validation_data=(np.array(x_test), np.array(y_test)))

#有區分有花無花的結果+沒有取眾數
loss, accuracy = model.evaluate(np.array(x_test), np.array(y_test), verbose=0)
print(classes_pic_num)
print('Test loss:', loss)
print('Test accuracy(還沒取眾數前 / 有分有沒有開花):', accuracy)
#沒有區分有花沒有花的結果
prediction = model.predict(np.array(x_test))
prediction_classes = np.argmax(prediction,axis=1)

#沒有區分有花無花的結果+沒有取眾數
correct_count = 0
error_count = 0
start_index = 0
for class_index in range(len(classname)//2):
    end_index = start_index + (classes_pic_num[(class_index*2)])*(digits_in_img) + (classes_pic_num[class_index*2+1])*(digits_in_img)
    for pic_index in range(start_index,end_index):
        if(prediction_classes[pic_index]==class_index*2 or prediction_classes[pic_index] == class_index*2+1):
            correct_count = correct_count+1
        else:
            error_count = error_count+1
    start_index = end_index
print("Test accuracy(還沒取眾數前 / 不分有沒有開花):", float((correct_count)/len(prediction_classes)))





#有取眾數
#每張圖的預測結果有6個，所以要找出出現次數最多的類別(取眾數)
start_index=0
predict_classes_in_one = list() #放從6個選項中找出的最常出現的類別
ground_truth_in_one = list() #放真正的分類類別
for class_index in range(len(classname)):
    for prediction_index in range(classes_pic_num[class_index]):
        mode = get_mode(prediction_classes[start_index:(start_index+digits_in_img)])
        predict_classes_in_one.append(mode)
        ground_truth_in_one.append(class_index)
        start_index = start_index + digits_in_img

      
#計算有區分有沒有開花
correct_count = 0
error_count = 0
start_index = 0
for class_index in range(len(predict_classes_in_one)):
    if(predict_classes_in_one[class_index] == ground_truth_in_one[class_index]):
        correct_count = correct_count+1
    else :
        error_count = error_count +1
print("Test accuracy(有取眾數 / 有分有沒有開花):", float((correct_count)/len(predict_classes_in_one)))



#計算沒有分有沒有開花
correct_count = 0
error_count = 0
start_index = 0
for class_index in range(len(classname)//2):
    end_index = start_index + (classes_pic_num[(class_index*2)]) + (classes_pic_num[class_index*2+1])
    for pic_index in range(start_index,end_index):
        if(predict_classes_in_one[pic_index]==class_index*2 or predict_classes_in_one[pic_index] == class_index*2+1):
            correct_count = correct_count+1
        else:
            error_count = error_count+1
    start_index = end_index
print("Test accuracy(有取眾數 / 不分有沒有開花):", float((correct_count)/len(predict_classes_in_one)))


model.save('cnn_model.h5')
