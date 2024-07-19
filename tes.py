import RPi.GPIO as GPIO
import time

# GPIO 경고 비활성화
GPIO.setwarnings(False)

# GPIO 핀 번호 설정
SERVO_PIN = 17  # 서보 모터를 연결할 GPIO 핀 번호

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# PWM 설정
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz 주파수 설정
pwm.start(0)  # PWM 시작

def set_servo_angle(angle):
    duty = angle / 18 + 2  # Duty cycle 계산
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)  # Duty cycle 조정
    time.sleep(1)  # 서보가 각도로 이동할 시간
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

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

# 정리
pwm.stop()
GPIO.cleanup()
