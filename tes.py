#include <Servo.h>  // Servo 라이브러리 포함

Servo myServo;  // Servo 객체 생성

void setup() {
  myServo.attach(9);  // 서보를 디지털 핀 9에 연결
}

void loop() {
  // 0도에서 180도까지 서보 이동
  for (int pos = 0; pos <= 180; pos += 1) {
    myServo.write(pos);  // 서보를 pos도 위치로 이동
    delay(15);  // 이동 시간 지연
  }

  // 180도에서 0도까지 서보 이동
  for (int pos = 180; pos >= 0; pos -= 1) {
    myServo.write(pos);  // 서보를 pos도 위치로 이동
    delay(15);  // 이동 시간 지연
  }
}
