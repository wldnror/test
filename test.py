import bluetooth
import subprocess
from pydbus import SystemBus
from gi.repository import GLib

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

# 연결된 장치 목록
connected_devices = set()

# 블루투스 서버 소켓 설정
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)
port = server_sock.getsockname()[1]
print(f"Listening on port {port}")

# 장치 연결 상태 확인 함수
def check_device_connection():
    managed_objects = bus.get("org/bluez", "/").GetManagedObjects()
    new_connections = False
    for path, interfaces in managed_objects.items():
        if "org.bluez.Device1" in interfaces:
            device = interfaces["org.bluez.Device1"]
            if device["Connected"] and path not in connected_devices:
                connected_devices.add(path)
                print(f"Device connected: {path}")
                new_connections = True
                handle_connection()
    return True

# 연결된 장치와 데이터 송수신 처리 함수
def handle_connection():
    client_sock, client_info = server_sock.accept()
    print(f"Accepted connection from {client_info}")
    try:
        while True:
            data = client_sock.recv(1024).decode('utf-8')
            if data:
                print(f"Received: {data}")
                if data == "DROP_BATTERY":
                    print("Received command to drop battery")
                    # 모터 제어 대신 출력 메시지로 대체
                    print("Motor would be activated now (simulated)")
                    client_sock.send("Battery drop simulated".encode('utf-8'))
            if not data:
                break
    except OSError:
        pass
    print("Disconnected")
    client_sock.close()

# 주기적으로 장치 연결 상태 확인 (1초마다)
GLib.timeout_add_seconds(1, check_device_connection)

print("Waiting for connections...")

# 메인 루프 실행
GLib.MainLoop().run()

server_sock.close()
