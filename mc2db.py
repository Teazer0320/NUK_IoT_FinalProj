import time, random, requests
import DAN
import pymysql


def insert_mc_intoDB(data):
	db_settings = {
		"host": "127.0.0.1",
		"user": "elf",
		"password": "elfgroup4",
		"database": "elfdb",
	}
	db = pymysql.connect(**db_settings)
	cursor = db.cursor()
	
	# modify this
	cursor.execute("insert into plant_picture (machine_id, plant_pic) values(%s, %s);", ("FF:EE:AA:FF:CC:BB", pic_bin))
	db.commit()
	
	cursor.close()
	db.close()


ServerURL = 'http://2.iottalk.tw:9999'      #with non-secure connection
#ServerURL = 'https://DomainName' #with SSL connection
Reg_addr = None #if None, Reg_addr = MAC address

DAN.profile['dm_name']='Dummy_Device'
DAN.profile['df_list']=['Dummy_Sensor', 'Dummy_Control',]
#DAN.profile['d_name']= 'Assign a Device Name' 

DAN.device_registration_with_retry(ServerURL, Reg_addr)
#DAN.deregister()  #if you want to deregister this device, uncomment this line
#exit()            #if you want to deregister this device, uncomment this line

while True:
    try:
        IDF_data = random.uniform(1, 10)
        DAN.push ('Dummy_Sensor', IDF_data) #Push data to an input device feature "Dummy_Sensor"
        print('put'+str(IDF_data))
        #==================================

        ODF_data = DAN.pull('Dummy_Control')#Pull data from an output device feature "Dummy_Control"
        if ODF_data != None:
            print ('get'+str(ODF_data[0]))   #print (ODF_data[0])

    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)    

    time.sleep(0.2)

