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

# 블루투스 서버 소켓 설정
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)
port = server_sock.getsockname()[1]
print(f"Listening on port {port}")

def handle_connection(client_sock):
    try:
        print(f"Accepted connection from {client_sock.getpeername()}")
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
    except OSError as e:
        print(f"Connection error: {e}")
    finally:
        print("Disconnected")
        client_sock.close()

# 블루투스 연결 대기 및 처리
def wait_for_connections():
    while True:
        print("Waiting for new connection...")
        client_sock, client_info = server_sock.accept()
        handle_connection(client_sock)

print("Waiting for connections...")
wait_for_connections()
