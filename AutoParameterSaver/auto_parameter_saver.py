import os
import sys
import time
import datetime
import json
import struct
import csv
import paho.mqtt.client as mqtt

# 設定系変数(デフォルト値で初期化)
MQTT_BROKER_IP = "DEVNOTEPC"
MQTT_BROKER_PORT = 1883
VAL_NUM = 400

val_num_list = list(range(400))
val_list = [0] * VAL_NUM
val_type_list = [""] * VAL_NUM
val_name_list = [""] * VAL_NUM

def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
        MQTT_BROKER_IP = config["MQTT_BROKER_IP"]
        MQTT_BROKER_PORT = config["MQTT_BROKER_PORT"]
        VAL_NUM = config["VAL_NUM"]


def load_val_name_list():
    global val_name_list
    with open('val_name_list.json', 'r') as f:        
        val_name_list = json.load(f)["val_name_list"]
def on_message(client, userdata, msg):    
    if msg.topic == "mouse":
        check_sum = 0
        for i in range(7,400):
            check_sum += msg.payload[i]
        check_sum = check_sum % 256
        if check_sum != msg.payload[6]:
            print("check_sum error!")
            return


        part_num = msg.payload[250]
        for i in range(10):
            val_num = part_num * 10 + i
            type_index_num = 250 + 2 + i * 5
            val_index_num = type_index_num + 1            
            val_type = msg.payload[type_index_num]
            v0 = msg.payload[val_index_num + 0]
            v1 = msg.payload[val_index_num + 1]
            v2 = msg.payload[val_index_num + 2] 
            v3 = msg.payload[val_index_num + 3]
            
            if val_type == 0:
                val_type_list[val_num] = "float"
                int_pack = v0 + (v1 << 8) + (v2 << 16) + (v3 << 24)
                val_list[val_num] = struct.unpack('<f',struct.pack('<L',int_pack))[0]
            elif val_type == 1:
                val_type_list[val_num] = "uint8"
                val_list[val_num] = v0
            elif val_type == 2:
                val_type_list[val_num] = "uint16"
                val_list[val_num] = v0 + (v1 << 8)
            elif val_type == 3:
                val_type_list[val_num] = "uint32"
                val_list[val_num] = v0 + (v1 << 8) + (v2 << 16) + (v3 << 24)
            elif val_type == 4:
                val_type_list[val_num] = "int8"
                val_list[val_num] = v0
                if val_list[val_num] > 127:
                    val_list[val_num] = val_list[val_num] - 128
            elif val_type == 5:
                val_type_list[val_num] = "int16"
                val_list[val_num] = v0 + (v1 << 8)
                if val_list[val_num] > 32767:
                    val_list[val_num] = val_list[val_num] - 32768
            elif val_type == 6:
                val_type_list[val_num] = "int32"
                val_list[val_num] = v0 + (v1 << 8) + (v2 << 16) + (v3 << 24)
                if val_list[val_num] > 2147483647:
                    val_list[val_num] = val_list[val_num] - 2147483648
            else:
                val_type_list[val_num] = "none"
                val_name_list[val_num] = "none"               
                val_list[val_num] = 0
            # print (val_num, val_name_list[val_num], val_type_list[val_num] ,val_list[val_num])



def create_mqtt_client():
    host = MQTT_BROKER_IP
    port = MQTT_BROKER_PORT

    # インスタンス作成時に protocl v3.1.1を指定
    client = mqtt.Client(protocol=mqtt.MQTTv311)

    client.connect(host, port=port, keepalive=60)
    client.publish("presence","this is " + __file__)
    client.on_message = on_message 
    client.subscribe("mouse")
    return client

def write_csv(contents):
    dt_now = datetime.datetime.now()
    file_name =  "./saved_data/" + dt_now.strftime('%Y%m%d_%H%M%S_param') + ".csv"

    with open(file_name, "w") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(contents) # csvファイルに書き込み

def is_all_param_recieved():
    not_recieved = False
    for ele in val_type_list:
        if ele == "":
            not_recieved = True
    return (not not_recieved)

def is_param_changed(now, pre):
    if now == pre:
        return False
    else:
        return True

def main():
    # コンフィグファイルの読み込み
    load_config()
    load_val_name_list()      

    # MQTTクライアントの初期化
    client = create_mqtt_client()
    client.loop_start()
    csv_contents_pre = None    
    while True:        
        time.sleep(1)      
        csv_contents_now = list(zip(*[val_num_list, val_name_list, val_type_list, val_list]))
        changed = is_param_changed(csv_contents_now, csv_contents_pre)
        
        csv_contents_pre = list(zip(*[val_num_list, val_name_list, val_type_list, val_list]))

        if is_all_param_recieved() == True and changed == True:
            print("param changed!")
            write_csv(csv_contents_now)
                


if __name__ == "__main__":
    main()