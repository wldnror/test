import RPi.GPIO as GPIO
import time

# GPIO 핀 번호
MOTOR_PIN_1 = 18
MOTOR_PIN_2 = 5

# GPIO 설정
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN_1, GPIO.OUT)
GPIO.setup(MOTOR_PIN_2, GPIO.OUT)

# 서보 모터 제어를 위한 PWM 설정
pwm1 = GPIO.PWM(MOTOR_PIN_1, 50)  # 50Hz PWM 신호
pwm2 = GPIO.PWM(MOTOR_PIN_2, 50)  # 50Hz PWM 신호

pwm1.start(0)
pwm2.start(0)

def set_angle(pwm, angle):
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)  # 서보 모터가 목표 각도에 도달할 시간을 줌
    pwm.ChangeDutyCycle(0)

try:
    while True:
        # 0도로 설정
        print("Setting angle to 0 degrees")
        set_angle(pwm1, 0)
        set_angle(pwm2, 0)
        time.sleep(2)

        # 90도로 설정 (기본 위치)
        print("Setting angle to 90 degrees (center position)")
        set_angle(pwm1, 90)
        set_angle(pwm2, 90)
        time.sleep(2)

        # 180도로 설정
        print("Setting angle to 180 degrees")
        set_angle(pwm1, 180)
        set_angle(pwm2, 180)
        time.sleep(2)

except KeyboardInterrupt:
    pass
finally:
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
