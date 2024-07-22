import RPi.GPIO as GPIO
import time
import curses

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
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

# 초기 각도 설정
angle1 = 90
angle2 = 90
set_angle(pwm1, angle1)
set_angle(pwm2, angle2)

def main(stdscr):
    global angle1, angle2
    
    curses.curs_set(0)  # 커서 숨기기
    stdscr.nodelay(1)   # 비차단 모드
    stdscr.timeout(100) # 100ms마다 화면 갱신

    while True:
        key = stdscr.getch()

        if key == ord('a'):  # 좌측으로 이동
            angle1 = max(0, angle1 - 10)
            angle2 = max(0, angle2 - 10)
            set_angle(pwm1, angle1)
            set_angle(pwm2, angle2)
            stdscr.addstr(0, 0, f"Motor 1 angle: {angle1}, Motor 2 angle: {angle2}")
            stdscr.refresh()

        elif key == ord('d'):  # 우측으로 이동
            angle1 = min(180, angle1 + 10)
            angle2 = min(180, angle2 + 10)
            set_angle(pwm1, angle1)
            set_angle(pwm2, angle2)
            stdscr.addstr(0, 0, f"Motor 1 angle: {angle1}, Motor 2 angle: {angle2}")
            stdscr.refresh()

        elif key == ord('q'):  # 프로그램 종료
            break

        time.sleep(0.1)  # 키 입력 딜레이

try:
    curses.wrapper(main)
except KeyboardInterrupt:
    pass
finally:
    # 종료
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
