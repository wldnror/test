import pigpio
import time

# GPIO 핀 번호 설정
SERVO_PIN = 17  # 서보 모터를 연결할 GPIO 핀 번호

# pigpio 설정
pi = pigpio.pi()

# 서보 제어 함수
def set_servo_angle(angle):
    # 서보의 각도에 따라 펄스 폭을 계산
    pulse_width = 500 + (angle / 180) * 2000
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)
    time.sleep(1)  # 서보가 각도로 이동할 시간

try:
    while True:
        # 0도에서 180도까지 서보 모터를 이동
        for angle in range(0, 181, 10):
            set_servo_angle(angle)
            time.sleep(0.5)
        
        # 180도에서 0도까지 서보 모터를 이동
        for angle in range(180, -1, -10):
            set_servo_angle(angle)
            time.sleep(0.5)

except KeyboardInterrupt:
    pass

# 서보 정리
pi.set_servo_pulsewidth(SERVO_PIN, 0)
pi.stop()
