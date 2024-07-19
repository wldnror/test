import bluetooth
import subprocess
from pydbus import SystemBus
from gi.repository import GLib
import RPi.GPIO as GPIO
import time

# GPIO 설정
MOTOR_PIN_1 = 17  # 첫 번째 모터 핀
MOTOR_PIN_2 = 18  # 두 번째 모터 핀

GPIO.setwarnings(False)  # 경고 비활성화
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN_1, GPIO.OUT)
GPIO.setup(MOTOR_PIN_2, GPIO.OUT)

pwm1 = GPIO.PWM(MOTOR_PIN_1, 50)  # 50Hz PWM 신호
pwm2 = GPIO.PWM(MOTOR_PIN_2, 50)

pwm1.start(0)
pwm2.start(0)

def set_motor_angle(pwm, angle):
    duty = angle / 18 + 2
    GPIO.output(MOTOR_PIN_1, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(MOTOR_PIN_1, False)
    pwm.ChangeDutyCycle(0)

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
    try:
        managed_objects = bus.get("org.bluez", "/").GetManagedObjects()
        new_connections = False
        for path, interfaces in managed_objects.items():
            if "org.bluez.Device1" in interfaces:
                device = interfaces["org.bluez.Device1"]
                if device["Connected"] and path not in connected_devices:
                    connected_devices.add(path)
                    print(f"Device connected: {path}")
                    new_connections = True
                    handle_connection()
    except Exception as e:
        print(f"Error checking device connection: {e}")
    return True

# 연결된 장치와 데이터 송수신 처리 함수
def handle_connection():
    client_sock, client_info = server_sock.accept()
    print(f"Accepted connection from {client_info}")
    try:
        while True:
            print("Waiting for data...")
            data = client_sock.recv(1024)
            if data:
                decoded_data = data.decode('utf-8')
                print(f"Received: {decoded_data}")
                if decoded_data == "DROP_BATTERY":
                    print("Received command to drop battery")
                    # 두 모터를 동시에 제어
                    print("Setting motor angles to 90 degrees")  # 모터 제어 시각적 표시
                    set_motor_angle(pwm1, 90)  # 각도를 90도로 설정 (예시)
                    set_motor_angle(pwm2, 90)
                    client_sock.send("Battery drop simulated".encode('utf-8'))
            if not data:
                break
    except OSError as e:
        print(f"OSError: {e}")
    print("Disconnected")
    client_sock.close()

# 주기적으로 장치 연결 상태 확인 (1초마다)
GLib.timeout_add_seconds(1, check_device_connection)

print("Waiting for connections...")

# 메인 루프 실행
GLib.MainLoop().run()

# 청소
server_sock.close()
pwm1.stop()
pwm2.stop()
GPIO.cleanup()
