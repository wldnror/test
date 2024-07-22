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
    time.sleep(0.5)  # 서보 모터가 목표 각도에 도달할 시간을 줌
    pwm.ChangeDutyCycle(0)

def main(stdscr):
    curses.curs_set(1)  # 커서 보이기
    stdscr.nodelay(0)   # 차단 모드 (사용자 입력 기다림)

    angle1 = 90
    angle2 = 90
    set_angle(pwm1, angle1)
    set_angle(pwm2, angle2)

    stdscr.addstr(0, 0, "서보 모터 제어 프로그램")
    stdscr.addstr(1, 0, "각도를 입력하고 Enter를 누르세요 (0-180)")
    stdscr.addstr(3, 0, f"현재 Motor 1 각도: {angle1}")
    stdscr.addstr(4, 0, f"현재 Motor 2 각도: {angle2}")

    while True:
        stdscr.addstr(6, 0, "Motor 1 각도 변경 (시계 반대: 음수, 시계: 양수): ")
        curses.echo()
        angle1_change = stdscr.getstr(6, 43, 4).decode('utf-8')
        curses.noecho()

        stdscr.addstr(7, 0, "Motor 2 각도 변경 (시계 반대: 음수, 시계: 양수): ")
        curses.echo()
        angle2_change = stdscr.getstr(7, 43, 4).decode('utf-8')
        curses.noecho()

        try:
            angle1 = angle1 + int(angle1_change)
            angle2 = angle2 + int(angle2_change)
            if 0 <= angle1 <= 180 and 0 <= angle2 <= 180:
                set_angle(pwm1, angle1)
                set_angle(pwm2, angle2)
                stdscr.addstr(3, 0, f"현재 Motor 1 각도: {angle1}    ")
                stdscr.addstr(4, 0, f"현재 Motor 2 각도: {angle2}    ")
            else:
                stdscr.addstr(8, 0, "각도는 0에서 180 사이여야 합니다. ")
        except ValueError:
            stdscr.addstr(8, 0, "유효한 숫자를 입력하세요.          ")

        stdscr.addstr(9, 0, "프로그램을 종료하려면 'q'를 누르세요.")
        stdscr.refresh()

        # 'q' 키 입력시 프로그램 종료
        key = stdscr.getch()
        if key == ord('q'):
            break

try:
    curses.wrapper(main)
except KeyboardInterrupt:
    pass
finally:
    # 종료
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
