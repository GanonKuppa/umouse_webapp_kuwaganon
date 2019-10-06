rem テスト用アプリを一括起動

call forever stopall
rem 起動済みアプリを一括停止

pushd ..\Serial2MQTT_python
call forever start -c python serial2mqtt.py
rem serial2mqttを起動
poped

pushd ..\AutoParameterSaver
call forever start -c python auto_parameter_saver.py
rem AutoParameterSaverを起動
poped


pushd ..\xinput_gamepad2MQTT_python
call forever start -c python xinputgamepad2MQTT.py
rem gamepadを起動
popd

pushd ..\umouse_webapp
call forever start app.js
rem webサーバを起動
popd

call forever list

start mosquitto
rem mqttブローカーを起動


pause

