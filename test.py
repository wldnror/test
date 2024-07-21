import bluetooth
import subprocess
import socket
from pydbus import SystemBus
from gi.repository import GLib
import netifaces
import time
import os
import RPi.GPIO as GPIO
from flask import Flask, request, jsonify

app = Flask(__name__)

# 로컬 머신의 IP 주소를 가져오는 함수
def get_local_ip():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        if interface == 'lo':
            continue
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            ip_info = addrs[netifaces.AF_INET][0]
            ip = ip_info['addr']
            return ip
    return "IP 주소를 가져올 수 없습니다"

# D-Bus 연결 설정
bus = SystemBus()

# 블루투스 어댑터 가져오기
adapter_path = "/org/bluez/hci0"
adapter = bus.get("org.bluez", adapter_path)

# 블루투스 어댑터를 Discoverable로 설정
discovery_filter = {
    "Transport": GLib.Variant("s", "auto")
}
adapter.SetDiscoveryFilter(discovery_filter)
adapter.Powered = True
adapter.Discoverable = True
adapter.Pairable = True

# 블루투스 서버 소켓 설정
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)
port = server_sock.getsockname()[1]
print(f"Listening on port {port}")

# 현재 스크립트의 디렉토리 경로 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
sound_file_path = os.path.join(script_dir, "alert-sound.mp3")

# 모터 제어 핀 설정
MOTOR_PIN_1 = 18  # GPIO 핀 번호
MOTOR_PIN_2 = 5  # GPIO 핀 번호

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN_1, GPIO.OUT)
GPIO.setup(MOTOR_PIN_2, GPIO.OUT)

# PWM 설정
pwm_motor_1 = GPIO.PWM(MOTOR_PIN_1, 50)  # 50Hz
pwm_motor_2 = GPIO.PWM(MOTOR_PIN_2, 50)  # 50Hz
pwm_motor_1.start(0)
pwm_motor_2.start(0)

def set_motor_angle(pwm, pin, angle):
    duty = angle / 18 + 2
    GPIO.output(pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(pin, False)
    pwm.ChangeDutyCycle(0)

def handle_connection(client_sock):
    try:
        print(f"Accepted connection from {client_sock.getpeername()}")

        # 로컬 IP 주소 전송
        local_ip = get_local_ip()
        client_sock.send(f"LOCAL_IP:{local_ip}".encode('utf-8'))
        print(f"Sent local IP: {local_ip}")

        while True:
            data = client_sock.recv(1024).decode('utf-8')
            print(f"Data received: {data}")
            if data:
                print(f"Received: {data}")
                if data == "DROP_BATTERY":
                    print("Received command to drop battery")
                    # 사운드 파일 재생
                    subprocess.run(["mpg123", sound_file_path], check=True)

                    # 모터 제어
                    print("Activating motors")
                    set_motor_angle(pwm_motor_1, MOTOR_PIN_1, 90)  # 90도로 회전
                    set_motor_angle(pwm_motor_2, MOTOR_PIN_2, 90)  # 90도로 회전
                    client_sock.send("Battery drop simulated".encode('utf-8'))
                elif data == "GIT_PULL":
                    print("Received command to git pull")
                    subprocess.run(["git", "pull"], check=True)
                    client_sock.send("Git pull executed".encode('utf-8'))
                    print("Git pull executed, restarting script...")
                    subprocess.Popen(["python3", os.path.abspath(__file__)])  # 스크립트 재시작
                    os._exit(0)  # 현재 스크립트 종료
                elif data == "REBOOT":
                    print("Received command to reboot")
                    subprocess.run(["sudo", "reboot"], check=True)
                    client_sock.send("Reboot executed".encode('utf-8'))
            if not data:
                break
    except OSError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Disconnected")
        client_sock.close()

def wait_for_connections():
    while True:
        print("Waiting for new connection...")
        client_sock, client_info = server_sock.accept()
        print(f"Connection established with {client_info}")
        handle_connection(client_sock)

@app.route('/execute_command', methods=['GET'])
def execute_command():
    command = request.args.get('command')
    if command:
        print(f"Executing command: {command}")
        if command == "git pull":
            subprocess.run(["git", "pull"], check=True)
            print("Git pull executed, restarting script...")
            subprocess.Popen(["python3", os.path.abspath(__file__)])  # 스크립트 재시작
            os._exit(0)  # 현재 스크립트 종료
            return "Git pull executed, restarting script...", 200
        elif command == "sudo reboot":
            subprocess.run(["sudo", "reboot"], check=True)
            return "Reboot executed", 200
        else:
            return "Unknown command", 400
    else:
        return "No command provided", 400

if __name__ == '__main__':
    import threading
    try:
        # 모터 초기화
        set_motor_angle(pwm_motor_1, MOTOR_PIN_1, 0)  # 초기화 위치
        set_motor_angle(pwm_motor_2, MOTOR_PIN_2, 0)  # 초기화 위치

        # Flask 서버를 별도의 스레드에서 실행
        flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
        flask_thread.start()
        
        # 블루투스 연결 대기
        wait_for_connections()
    finally:
        pwm_motor_1.stop()
        pwm_motor_2.stop()
        GPIO.cleanup()
