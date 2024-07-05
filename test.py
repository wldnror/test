import bluetooth

# 블루투스 서버 설정
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

bluetooth.advertise_service(server_sock, "BatteryDropper",
                            service_id="00001101-0000-1000-8000-00805F9B34FB",
                            service_classes=["00001101-0000-1000-8000-00805F9B34FB"])

print(f"Waiting for connection on RFCOMM channel {port}")

client_sock, client_info = server_sock.accept()
print(f"Accepted connection from {client_info}")

try:
    while True:
        data = client_sock.recv(1024).decode('utf-8')
        if data == "DROP_BATTERY":
            print("Received command to drop battery")
            # 여기서 모터 제어 대신 출력 메시지로 대체
            print("Motor would be activated now (simulated)")
        if not data:
            break
except OSError:
    pass

print("Disconnected")

client_sock.close()
server_sock.close()
