import sys
import ctypes
import time
import json
import paho.mqtt.client as mqtt


# DXライブラリ関係定数
DX_INPUT_PAD1 = (0x0001)
DX_INPUT_PAD2 = (0x0002)
DX_INPUT_PAD3 = (0x0003)
DX_INPUT_PAD4 = (0x0004)

XINPUT_BUTTON_DPAD_UP = 0 # デジタル方向ボタン上
XINPUT_BUTTON_DPAD_DOWN = 1 # デジタル方向ボタン下
XINPUT_BUTTON_DPAD_LEFT = 2 # デジタル方向ボタン左
XINPUT_BUTTON_DPAD_RIGHT = 3 # デジタル方向ボタン右
XINPUT_BUTTON_START = 4 # STARTボタン
XINPUT_BUTTON_BACK = 5 # BACKボタン
XINPUT_BUTTON_LEFT_THUMB = 6 # 左スティック押し込み
XINPUT_BUTTON_RIGHT_THUMB = 7 # 右スティック押し込み
XINPUT_BUTTON_LEFT_SHOULDER = 8 # LBボタン
XINPUT_BUTTON_RIGHT_SHOULDER = 9 # RBボタン
XINPUT_BUTTON_A = 12 # Aボタン
XINPUT_BUTTON_B = 13 # Bボタン
XINPUT_BUTTON_X = 14 # Xボタン
XINPUT_BUTTON_Y = 15 # Yボタン

# 設定系変数(デフォルト値で初期化)
MQTT_BROKER_IP = "DEVNOTEPC"
MQTT_BROKER_PORT = 1883
LOOP_TIME = 0.02
RECONECT_GAMEPAD_RETRY_TIME = 3

#
class XInputState(ctypes.Structure):
    _fields_ = [
        ("Buttons", ctypes.c_ubyte * 16),
        ("LeftTrigger", ctypes.c_ubyte),
        ("RightTrigger", ctypes.c_ubyte),
        ("ThumbLX", ctypes.c_short),
        ("ThumbLY", ctypes.c_short),
        ("ThumbRX", ctypes.c_short),
        ("ThumbRY", ctypes.c_short)
    ]

# グローバル変数
dxlib = ctypes.cdll.DxLib_x64
c_lib = ctypes.cdll.msvcrt
x_input_state = XInputState()
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
    "Y":0,
    "X":0,
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
    LOOP_TIME = config["LOOP_TIME"]
    RECONECT_GAMEPAD_RETRY_TIME = config["RECONECT_GAMEPAD_RETRY_TIME"]



def set_gamepad_input2key_dict():
    rx, ry, lx, ly = clip_3Dpad_output()
    key_dict["R3D_x"] = rx
    key_dict["R3D_y"] = ry
    key_dict["L3D_x"] = lx
    key_dict["L3D_y"] = ly

    key_dict["A"] = x_input_state.Buttons[XINPUT_BUTTON_A]
    key_dict["B"] = x_input_state.Buttons[XINPUT_BUTTON_B]
    key_dict["X"] = x_input_state.Buttons[XINPUT_BUTTON_X]
    key_dict["Y"] = x_input_state.Buttons[XINPUT_BUTTON_Y]
    key_dict["RB"] = x_input_state.Buttons[XINPUT_BUTTON_RIGHT_SHOULDER]
    key_dict["LB"] = x_input_state.Buttons[XINPUT_BUTTON_LEFT_SHOULDER]
    key_dict["RT"] = x_input_state.RightTrigger
    key_dict["LT"] = x_input_state.LeftTrigger

    key_dict["BACK"] = x_input_state.Buttons[XINPUT_BUTTON_BACK]
    key_dict["START"] = x_input_state.Buttons[XINPUT_BUTTON_START]

    cross_x, cross_y = clip_cross_button_output()
    key_dict["cross_x"] = cross_x
    key_dict["cross_y"] = cross_y

   

def create_mqtt_client():
    host = MQTT_BROKER_IP
    port = MQTT_BROKER_PORT

    # インスタンス作成時に protocl v3.1.1を指定
    client = mqtt.Client(protocol=mqtt.MQTTv311)

    client.connect(host, port=port, keepalive=60)
    client.publish("presence","this is " + __file__)
    return client




def draw_string(x, y, str):
    white = dxlib.dx_GetColor(255,255,255)
    b_str = str.encode("UTF-8")
    s = ctypes.create_string_buffer(255)
    c_lib.sprintf(s, b'%s', b_str)

    dxlib.dx_DrawString(x, y ,s, white)

def set_main_window_text(str):
    b_str = str.encode("UTF-8")
    s = ctypes.create_string_buffer(255)
    c_lib.sprintf(s, b'%s', b_str)

    dxlib.dx_SetMainWindowText(s)


def clip_3Dpad_output():
    rx = int((x_input_state.ThumbRX - 128)/128) + 128
    if(rx > 255):
        rx = 255
    if(rx < 0):
        rx = 0
    if(118 < rx < 138):
        rx = 128

    ry = int((x_input_state.ThumbRY - 128)/128) + 128
    if(ry > 255):
        ry = 255
    if(ry < 0):
        ry = 0
    if(118 < ry < 138):
        ry = 128

    lx = int((x_input_state.ThumbLX - 128)/128) + 128
    if(lx > 255):
        lx = 255
    if(lx < 0):
        lx = 0
    if(118 < lx < 138):
        lx = 128


    ly = int((x_input_state.ThumbLY - 128)/128) + 128 
    if(ly > 255):
        ly = 255
    if(ly < 0):
        ly = 0
    if(118 < ly < 138):
        ly = 128
    

    return (rx, ry, lx, ly)

def clip_cross_button_output():
    cross_x = 128
    cross_y = 128

    if x_input_state.Buttons[XINPUT_BUTTON_DPAD_LEFT] == 1:
        cross_x = 129
    elif x_input_state.Buttons[XINPUT_BUTTON_DPAD_RIGHT] == 1:
        cross_x = 127

    if x_input_state.Buttons[XINPUT_BUTTON_DPAD_UP] == 1:
        cross_y = 129
    elif x_input_state.Buttons[XINPUT_BUTTON_DPAD_DOWN] == 1:
        cross_y = 127

    return (cross_x, cross_y)

def draw_gamepad_output():
    rx, ry, lx, ly = clip_3Dpad_output()

    draw_string(10, 10, "3DRX :" + str(rx))
    draw_string(10, 30, "3DRY :" + str(ry))
    draw_string(10, 50, "3DLX :" + str(lx))
    draw_string(10, 70, "3DLY :" + str(ly))

    draw_string(10, 90, "RT   :" + str(x_input_state.RightTrigger))
    draw_string(10, 110, "LT   :" + str(x_input_state.LeftTrigger))

    cross_x, cross_y = clip_cross_button_output()
    draw_string(10, 150, "CROSS_X:" + str(cross_x))
    draw_string(10, 170, "CROSS_Y:" + str(cross_y))

    draw_string(10, 210, "START:" + str(x_input_state.Buttons[XINPUT_BUTTON_START]))
    draw_string(10, 230, "BACK :" + str(x_input_state.Buttons[XINPUT_BUTTON_BACK]))

    draw_string(10, 250, "3DRB :" + str(x_input_state.Buttons[XINPUT_BUTTON_RIGHT_THUMB]))
    draw_string(10, 270, "3DLB :" + str(x_input_state.Buttons[XINPUT_BUTTON_LEFT_THUMB]))
    draw_string(10, 290, "LB   :" + str(x_input_state.Buttons[XINPUT_BUTTON_LEFT_SHOULDER]))
    draw_string(10, 310, "RB   :" + str(x_input_state.Buttons[XINPUT_BUTTON_RIGHT_SHOULDER]))
    draw_string(10, 330, "A    :" + str(x_input_state.Buttons[XINPUT_BUTTON_A]))
    draw_string(10, 350, "B    :" + str(x_input_state.Buttons[XINPUT_BUTTON_B]))
    draw_string(10, 370, "X    :" + str(x_input_state.Buttons[XINPUT_BUTTON_X]))
    draw_string(10, 390, "Y    :" + str(x_input_state.Buttons[XINPUT_BUTTON_Y]))

 
def init_DXlib():
    dxlib.dx_ChangeWindowMode(1) # 全画面表示をOFFに設定
    dxlib.dx_SetAlwaysRunFlag(1) # ウィンドウが非アクティブでも動作に設定
    if dxlib.dx_DxLib_Init() == -1:
        return False
    else:
        dxlib.dx_SetDrawScreen(-2)  # DX_SCREEN_BACK = -2
        set_main_window_text("xinput gamepad to MQTT") # ウィンドウのタイトルを設定
        return True

def end_DXlib():
    dxlib.dx_DxLib_End()
    

def main():
    # コンフィグファイルの読み込み
    load_config()

    # DXライブラリの初期化    
    while True: 
        result = init_DXlib() 
        if result == True:
            print("DXライブラリの初期化成功")
            break
        else:
            print("DXライブラリの初期化失敗")

    # MQTTクライアントの初期化
    client = create_mqtt_client()


    # 描画ループ
    fetch_time = 0
    sleep_time = 0
    loop_time = 0
    while dxlib.dx_ProcessMessage() == 0:
        fetch_start_time = time.time()
        dxlib.dx_ClearDrawScreen()
        
        result = dxlib.dx_GetJoypadXInputState(DX_INPUT_PAD1, ctypes.byref(x_input_state))
        if result == 0:
            print("読み取り成功")

            draw_gamepad_output()
            set_gamepad_input2key_dict()
            client.publish("gamepad", json.dumps(key_dict))
            draw_string(200, 10, "FETCH_TIME:" + str(fetch_time))
            draw_string(200, 30, "SLEEP_TIME:" + str(sleep_time))
            draw_string(200, 50, "LOOP_TIME :" + str(loop_time))


            dxlib.dx_ScreenFlip()
            
            fetch_end_time = time.time()
            fetch_time = fetch_end_time - fetch_start_time            
            sleep_time = LOOP_TIME - fetch_time
            loop_time = fetch_time + sleep_time

            if sleep_time > 0:
                time.sleep(sleep_time)
            print(fetch_time, sleep_time, loop_time)

        elif result == -1:
            print("読み取り失敗")
            print("DXライブラリを再初期化します")

            end_DXlib()
            time.sleep(RECONECT_GAMEPAD_RETRY_TIME)
            init_DXlib()
    
    end_DXlib()    
        



if __name__ == '__main__':
    main()



