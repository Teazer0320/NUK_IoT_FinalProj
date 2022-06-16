import time, random, requests
import DAN2
import pymysql
from sys import argv

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
	cursor.execute("UPDATE current_env SET humidity = %s WHERE plant_id = %s ;", (data[1]), data[0])
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


ServerURL = 'http://2.iottalk.tw:9999'      #with non-secure connection
#ServerURL = 'https://DomainName' #with SSL connection
Reg_addr = None #if None, Reg_addr = MAC address

DAN2.profile['dm_name']='MC2DB'
DAN2.profile['df_list']=['moisture', 'water_control',]
#DAN2.profile['d_name']= 'Assign a Device Name' 

DAN2.device_registration_with_retry(ServerURL, Reg_addr)
if len(argv) >= 2:
	DAN2.deregister()  #if you want to deregister this device, uncomment this line
	exit()            #if you want to deregister this device, uncomment this line

plant_type = 2
operation = 0
humidity = 0
moisture_record = list()
watering_record = list()
moisture_record.append(plant_type)
moisture_record.append(humidity)
watering_record.append(plant_type)
watering_record.append(operation)
watering_record.append(humidity)

while True:
    try:
        #IDF_data = random.uniform(1, 10)
        #DAN.push ('Dummy_Sensor', IDF_data) #Push data to an input device feature "Dummy_Sensor"
        #print('put'+str(IDF_data))
        #==================================
        ODF_data1 = DAN2.pull('moisture') #Pull data from an output device feature "Dummy_Control"
        ODF_data2 = DAN2.pull('water_control')
        if ODF_data1 != None:
            print('get moistrue:'+str(ODF_data1[0]))   #print (ODF_data[0])
            print('get water_control'+str(ODF_data2[0]))
            #傳回資料庫(不管有沒有要澆水)即時資料
            # 傳濕度(回傳值*100/1024)
            humidity = (int)((ODF_data1[0] * 100)/1024)
            moisture_record[1] = humidity
            insert_moisture_intoDB(moisture_record)

            if(ODF_data2 != None):
                print('get plant type...\n')
                if(ODF_data2[0]==1):
                    print("start watering...\n")
                    #傳回資料庫(有要澆水)照護資料
                    watering_record[1]=operation
                    watering_record[2]=humidity
                    insert_watering_intoDB(watering_record)


    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)    

    time.sleep(0.2)

