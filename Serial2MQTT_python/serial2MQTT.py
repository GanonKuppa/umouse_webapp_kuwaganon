#coding: UTF-8


import serial
import sys
import time
import binascii
import json
import math
from collections import deque
import paho.mqtt.client as mqtt

# 設定系変数(デフォルト値で初期化)
MQTT_BROKER_IP = "localhost"
MQTT_BROKER_PORT = 1883
SERIAL_PORT = "COM3"
MESSAGE_LEN = 400
NO_MESSAGE_TIME_OUT = 5.0
NO_MESSAGE_MAX_COUNT = 30000

# グローバル変数
cmd_gamepad = [99,109,100,254,253,252,0,0,0,128,128,128,128,128,128,252]
cmd_queue = deque([])
key_dict = {
    "cross_x":0,
    "cross_y":0,
    "L3D_x":0,
    "L3D_y":0,
    "R3D_x":0,
    "R3D_y":0,
    "RT":0,
    "LT":0,
    "A":0,
    "B":0,
    "X":0,
    "Y":0,
    "RB":0,
    "LB":0,
    "BACK":0,
    "START":0
}

def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    MQTT_BROKER_IP = config["MQTT_BROKER_IP"]
    MQTT_BROKER_PORT = config["MQTT_BROKER_PORT"]
    MESSAGE_LEN = config["MESSAGE_LEN"]
    NO_MESSAGE_TIME_OUT = config["NO_MESSAGE_TIME_OUT"]
    NO_MESSAGE_MAX_COUNT = config["NO_MESSAGE_MAX_COUNT"]


def on_message(client, userdata, msg):
    if msg.topic == "gamepad":
        cmd_byte = [0 for x in range(16)]
        key_dict = json.loads(msg.payload.decode('utf-8')  )
        cmd_byte[0] = 99 # ヘッダー
        cmd_byte[1] = 109
        cmd_byte[2] = 100
        cmd_byte[3] = 254# ID0
        cmd_byte[4] = 253 # ID1
        cmd_byte[9] = 128
        cmd_byte[10] = 128
        cmd_byte[11] = 128
        cmd_byte[12] = 128
        cmd_byte[13] = 128
        cmd_byte[14] = 128

        
        cmd_byte[6] = key_dict["A"] + \
                 (key_dict["B"] << 1) + \
                 (key_dict["X"] << 2) +\
                 (key_dict["Y"] << 3) +\
                 (key_dict["RB"] << 4) +\
                 (key_dict["LB"] << 5) +\
                 (key_dict["BACK"] << 6) +\
                 (key_dict["START"] << 7)
        cmd_byte[7] = key_dict["RT"]
        cmd_byte[8] = key_dict["LT"]

        cmd_byte[9] = key_dict["cross_x"]
        cmd_byte[10] = key_dict["cross_y"]
        cmd_byte[11] = key_dict["R3D_x"]
        cmd_byte[12] = key_dict["R3D_y"]
        cmd_byte[13] = key_dict["L3D_x"]
        cmd_byte[14] = key_dict["L3D_y"]
            
        cmd_byte[15] = 252

        chk_sum = 0
        for i in range(6,16):
            chk_sum += cmd_byte[i]
        cmd_byte[5] = chk_sum % 256 #  チェックサム


        global cmd_gamepad
        cmd_gamepad = [cmd_byte[i] for i in range(16)]


    if msg.topic == "cmd":
        global cmd_queue
        print(msg.payload)
        cmd_byte = [ msg.payload[i]  for i in range(16)  ]
        
        print(cmd_byte)
        cmd_queue.append(cmd_byte)
    
def create_mqtt_client():
    host = MQTT_BROKER_IP
    port = MQTT_BROKER_PORT

    # インスタンス作成時に protocl v3.1.1を指定
    client = mqtt.Client(protocol=mqtt.MQTTv311)

    client.connect(host, port=port, keepalive=60)
    client.publish("presence","this is " + __file__)
    client.on_message = on_message
    client.subscribe("gamepad")
    client.subscribe("cmd")

    return client


def publish_data_loop(client,ser):
    buff = []
    s = []
    st = []
    st_bytes=b""
    length = 0
    i      = 0
    start_time = time.time()
    timestamp = 0
    timestamp_pre = 0
    elapsed_time  = 0
    no_message_count = 0

    ser.write(cmd_gamepad)
    print (len(buff))
    while True:
        #client.publish("TEST","While Loop")
        s = [ele for ele in ser.read(ser.in_waiting)]
        buff.extend(s)
        if len(s) == 0:
            no_message_count = no_message_count + 1
            if no_message_count > NO_MESSAGE_MAX_COUNT:
                client.loop_stop(force=False)
                ser.close()
                print("COM" + " is busy.")
                client.publish("TEST", "Serial no message" +" error!")
                client.disconnect()
                print("exit!")
                sys.exit(0)
                return

        else:
            no_message_count = 0
        

        length = len(buff)
        if length < MESSAGE_LEN + 5:
            continue

        for i in range(length-MESSAGE_LEN-2):
            
            if  (buff[i] == 0xff)  and (buff[i+1] == 0xff) and \
                (buff[i+2]==0x48) and (buff[i+3]==0x45) and \
                (buff[i+4] == 0x41) and (buff[i+5]==0x44): #and \
                #(buff[i+message_len] == 0xff) and (buff[i+1+message_len] == 0xff):
                start_time = time.time()
                timestamp_pre = timestamp
                timestamp = buff[11]
                st = buff[i:i+MESSAGE_LEN]
                st_bytes = binascii.hexlify(bytes(list(st)))
                chk_sum = 0
                for k in range(7,MESSAGE_LEN):
                    chk_sum =  chk_sum + st[k]
                if chk_sum%256 != st[6] or (timestamp-timestamp_pre+256)%256 != 10:
                    client.publish("error", str(timestamp)+" "+str(timestamp_pre) + " " + str(chk_sum%256) + " " + str(st[6])+" "+ str(len(buff)))

                client.publish("mouse", bytes(list(st)))
                
                try:
                    ser.write(cmd_gamepad)
                    client.publish("TEST", "in msg loop")

                    if len(cmd_queue) != 0:
                        ser.write(cmd_queue.popleft())
                except:
                    ser.close()
                    client.publish("TEST", "serial write" +" error!")
                    return

                buff = buff[i+MESSAGE_LEN:]
                break
        end_time = time.time()       
        elapsed_time = end_time - start_time

        client.publish("TEST","elapsed:"+str(elapsed_time))


        #print (elapsed_time,len(buff),timestamp, (timestamp-timestamp_pre+256)%256  )
        #print(cmd_list)


        if(elapsed_time > NO_MESSAGE_TIME_OUT):
            client.loop_stop(force=False)
            ser.close()
            print("serial" + " is busy.")
            client.publish("TEST", "serial" +" is busy!")
            client.disconnect()
            print("exit!")
            sys.exit(0)
            return


def main():
    load_config()
    client = create_mqtt_client()
        
    while True:
        try:
            ser = serial.Serial(SERIAL_PORT,timeout = 0.05, write_timeout=0.05)
            client.publish("TEST", "Serial connected")
            print("Serial connected")
            break
        except:
            client.publish("TEST", "Cannot connect serial!")
            print("Cannot connect serial")
        
    client.publish("TEST", "data send start!")
  
    client.loop_start()

    publish_data_loop(client,ser)

if __name__ == "__main__":
    main()
