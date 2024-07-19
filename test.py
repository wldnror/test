import bluetooth
import subprocess
import socket
from pydbus import SystemBus
from gi.repository import GLib
import netifaces
import pygame
import time
import os
from flask import Flask, request

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

# 블루투스 장치 초기화
subprocess.run(["sudo", "hciconfig", "hci0", "up"], check=True)
subprocess.run(["sudo", "sdptool", "add", "SP"], check=True)

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

# pygame 초기화
pygame.mixer.init()

# 현재 스크립트의 디렉토리 경로 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
sound_file_path = os.path.join(script_dir, "alert-sound.mp3")

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
                    pygame.mixer.music.load(sound_file_path)
                    pygame.mixer.music.play()

                    # 사운드 파일이 끝날 때까지 대기
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)

                    # 모터 제어 대신 출력 메시지로 대체
                    print("Motor would be activated now (simulated)")
                    client_sock.send("Battery drop simulated".encode('utf-8'))
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
            return "Git pull executed", 200
        elif command == "sudo reboot":
            subprocess.run(["sudo", "reboot"], check=True)
            return "Reboot executed", 200
        else:
            return "Unknown command", 400
    else:
        return "No command provided", 400

if __name__ == '__main__':
    import threading
    # Flask 서버를 별도의 스레드에서 실행
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
    flask_thread.start()
    
    # 블루투스 연결 대기
    wait_for_connections()
