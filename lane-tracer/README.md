# Lane Tracer — RC Robot with ROS 2 + ESP32 micro-ROS

ROS 2 Jazzy 기반 PC와 ESP-IDF + micro-ROS 펌웨어를 올린 ESP32 사이를 UDP/Wi-Fi로 연결한
차선 추종 RC 로봇 프로젝트. Gazebo 시뮬레이션과 실제 하드웨어 양쪽 모두 지원하며,
ESP32 펌웨어는 Wi-Fi HTTPS OTA 업데이트가 가능합니다.

## 시스템 구성

```
   ┌──────────────────────────────────────────────────────────┐
   │                PC (Ubuntu 24.04, ROS 2 Jazzy)            │
   │                                                          │
   │   camera_node ──▶ /real/image_raw                        │
   │                          │                               │
   │                          ▼                               │
   │                   perception_node                        │
   │                          │                               │
   │                          ▼                               │
   │             /target_heading_error  (Float32)             │
   │             /perception/search_cmd (Int32)               │
   │                          │                               │
   │                          ▼                               │
   │                   micro-ROS Agent (UDP)                  │
   └──────────────────────────┬───────────────────────────────┘
                              │ Wi-Fi
   ┌──────────────────────────┴───────────────────────────────┐
   │            ESP32 (ESP-IDF v5.2 + micro-ROS)              │
   │   ─ L298N 모터 PID 제어 / 차선 추종 / 탐색 모드          │
   │   ─ MPU6050 IMU publish (/esp32/imu_debug)               │
   │   ─ 제어 상태 publish (/esp32/debug_status)              │
   │   ─ HTTPS OTA 클라이언트                                 │
   └──────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTPS
   ┌──────────────────────────┴───────────────────────────────┐
   │                    OTA Server (PC)                       │
   │   ─ UDP 19700 broadcast 응답 (서버 IP 자동 발견)         │
   │   ─ HTTPS 8000 포트로 firmware.bin 배포                  │
   └──────────────────────────────────────────────────────────┘
```

시뮬레이션 모드에서는 `camera_node` 대신 Gazebo의 `/image_raw` 토픽을 그대로 사용하고,
`sim_perception_node` + `sim_controller_node`가 ESP32 역할을 대체합니다.

## 디렉토리 구조

```
lane-tracer/
├── ros2_ws/src/tracer_pkg/   # ROS 2 패키지
│   ├── tracer_pkg/           #   Python 노드 (camera, perception, logger, sim)
│   ├── launch/               #   launch 파일들
│   ├── worlds/               #   Gazebo world
│   ├── models/lane_bot/      #   Gazebo 로봇 모델 + ArUco 텍스처
│   └── scripts/              #   ArUco 마커 생성 스크립트
├── esp32_firmware/           # ESP-IDF 프로젝트 (펌웨어)
│   ├── main/main.c
│   ├── CMakeLists.txt
│   ├── partitions.csv
│   └── sdkconfig.defaults
├── ota_server/               # OTA용 HTTPS 서버
│   └── https_server.py
└── docs/                     # 아키텍처, 토픽 명세, 셋업 가이드
    ├── architecture.md
    ├── topics.md
    ├── esp32_microros_setup_guide.md   # ESP-IDF + micro-ROS 환경 구축 가이드
    └── legacy/               # 초기 TCP 핸드셰이크 테스트 코드 (참고용)
```

## 의존성

### PC 측
- Ubuntu 24.04 (네이티브 또는 WSL2)
- ROS 2 **Jazzy**
- Python 3.12
- OpenCV (`opencv-contrib-python` — ArUco 모듈 필요)
- `cv_bridge`, `rclpy`
- Gazebo Harmonic + `ros_gz_bridge`
- [micro-ROS Agent](https://github.com/micro-ROS/micro-ros-agent)

### ESP32 측
- **ESP-IDF v5.2**
- [micro_ros_espidf_component](https://github.com/micro-ROS/micro_ros_espidf_component) (jazzy 브랜치)
- 하드웨어: ESP32 + L298N 모터 드라이버 + MPU6050 IMU

> 환경 구축은 [`docs/esp32_microros_setup_guide.md`](docs/esp32_microros_setup_guide.md)에 상세 가이드 있음.

## 빌드 및 실행

### 1. ROS 2 패키지 빌드

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/local_setup.bash
```

### 2. 실제 로봇 실행

```bash
# 터미널 1: micro-ROS Agent
ros2 run micro_ros_agent micro_ros_agent udp4 --port 8888

# 터미널 2: 카메라 + 퍼셉션
ros2 launch tracer_pkg lane_tracer.launch.py

# 로그 같이 남기고 싶다면
ros2 launch tracer_pkg lane_tracer.launch.py log:=true
```

로그는 `~/lane_tracer_logs/` 아래 CSV와 MP4로 저장됩니다.

### 3. Gazebo 시뮬레이션 실행

```bash
ros2 launch tracer_pkg gazebo_lane.launch.py
ros2 run tracer_pkg sim_perception_node
ros2 run tracer_pkg sim_controller_node
```

### 4. ESP32 펌웨어 빌드 & 플래시

```bash
cd esp32_firmware
. $HOME/esp/esp-idf/export.sh
idf.py set-target esp32
idf.py menuconfig    # Wi-Fi SSID/PW, micro-ROS Agent IP 설정
idf.py build
idf.py -p /dev/ttyUSB0 flash monitor
```

자세한 사용법은 [`esp32_firmware/README.md`](esp32_firmware/README.md) 참고.

### 5. OTA 서버 실행

```bash
cd ota_server
# 인증서 생성 (최초 1회)
openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout server.key -out server.crt -days 365 \
    -subj "/CN=lane-tracer-ota"
python3 https_server.py
```

자세한 OTA 사용법은 [`ota_server/README.md`](ota_server/README.md) 참고.

## 문서

- [`docs/architecture.md`](docs/architecture.md) — 노드 다이어그램, 데이터 흐름
- [`docs/topics.md`](docs/topics.md) — ROS 2 토픽 명세
- [`docs/esp32_microros_setup_guide.md`](docs/esp32_microros_setup_guide.md) — ESP-IDF + micro-ROS 환경 구축 가이드

## 라이선스

Apache-2.0
