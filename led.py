import board
import neopixel

# 설정 값
LED_COUNT = 300         # 네오픽셀의 수
LED_PIN = board.D18     # 데이터 핀 (보통 GPIO 18번 사용)
LED_BRIGHTNESS = 1.0    # 밝기 (0.0에서 1.0 사이)

# 네오픽셀 객체 생성
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# 모든 LED를 흰색으로 설정
pixels.fill((255, 255, 255))
pixels.show()

# 프로그램 종료 시 네오픽셀 끄기
try:
    while True:
        pass
except KeyboardInterrupt:
    pixels.fill((0, 0, 0))
    pixels.show()
