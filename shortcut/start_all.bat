rem �e�X�g�p�A�v�����ꊇ�N��

call forever stopall
rem �N���ς݃A�v�����ꊇ��~

pushd ..\Serial2MQTT_python
call forever start -c python serial2mqtt.py
rem serial2mqtt���N��
poped


pushd ..\xinput_gamepad2MQTT_python
call forever start -c python xinputgamepad2MQTT.py
rem gamepad���N��
popd

pushd ..\umouse_webapp
call forever start app.js
rem web�T�[�o���N��
popd

call forever list

start mosquitto
rem mqtt�u���[�J�[���N��


pause

