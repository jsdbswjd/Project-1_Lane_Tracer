# ESP32 Firmware (ESP-IDF + micro-ROS)

ESP32 측 펌웨어. micro-ROS 클라이언트로 PC의 micro-ROS Agent와 UDP 통신합니다.
또한 부팅 시 UDP broadcast로 OTA 서버를 자동 발견하여 HTTPS OTA 업데이트를 수행합니다.

## 의존성

- [ESP-IDF v5.2](https://docs.espressif.com/projects/esp-idf/en/v5.2/esp32/get-started/index.html)
- [micro_ros_espidf_component](https://github.com/micro-ROS/micro_ros_espidf_component) (jazzy 브랜치)
- 하드웨어: ESP32 DevKit + L298N 모터 드라이버 + MPU6050

> ESP-IDF v5.2 환경 구축 전체 가이드는 `../docs/esp32_microros_setup_guide.md` 참고.

## 초기 셋업

```bash
# ESP-IDF 환경 활성화 (.bashrc에 이미 alias 걸려있다면 생략)
. $HOME/esp/esp-idf/export.sh

# micro-ROS component 클론
mkdir -p components
cd components
git clone -b jazzy https://github.com/micro-ROS/micro_ros_espidf_component.git
cd ..
```

## 빌드 & 플래시

```bash
idf.py set-target esp32

# Wi-Fi SSID, password, micro-ROS Agent IP/Port 설정
idf.py menuconfig
#   - micro-ROS Settings  → micro-ROS Agent IP, Port
#   - (사용자 Wi-Fi 메뉴)   → SSID, Password

idf.py build
idf.py -p /dev/ttyUSB0 flash monitor
```

## OTA 업데이트

1. PC에서 `ota_server/https_server.py` 실행
2. 새 펌웨어 빌드 (`idf.py build`) 후 `build/lane_tracer_firmware.bin`을
   `ota_server/` 디렉토리에 `firmware.bin`이라는 이름으로 복사
3. ESP32 재부팅 또는 OTA 트리거 신호 → 자동으로 서버 IP를 발견하고 업데이트

## 파티션 구조

OTA를 위해 `ota_0`, `ota_1` 두 개의 app 파티션을 사용합니다.
세부 내용은 `partitions.csv` 참고.

## 트러블슈팅

- **Agent와 연결이 안 됨**: PC와 ESP32가 같은 Wi-Fi 네트워크에 있는지 확인.
  방화벽이 UDP 8888 (Agent) / 19700 (OTA 디스커버리) 포트를 막고 있지 않은지 확인.
- **OTA가 실패함**: `server.crt`가 ESP32에 임베드된 인증서와 일치하는지 확인.
  자체 서명 인증서를 새로 만들었다면 펌웨어 재빌드 필요.
