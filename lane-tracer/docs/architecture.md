# Architecture

## 노드 다이어그램

### 실제 로봇 모드 (`/real/...` 네임스페이스)

```
┌───────────────┐    /real/image_raw     ┌────────────────────┐
│ camera_node   │ ─────────────────────▶ │  perception_node   │
│ (USB webcam)  │                        │ (lane + ArUco)     │
└───────────────┘                        └─────────┬──────────┘
                                                   │
                  /real/path/lateral_error         │
                  /real/path/heading_error         │
                  /real/path/lookahead_error       │
                  /real/perception/search_cmd      │
                  /real/perception/debug_image     │
                  /real/perception/log_status      │
                                                   ▼
                                  (launch remap → ESP32 토픽)
                       /target_heading_error, /perception/search_cmd
                                                   │
                                                   ▼
                                         ┌────────────────────┐
                                         │  micro-ROS Agent   │
                                         │   (UDP 8888)       │
                                         └─────────┬──────────┘
                                                   │ Wi-Fi
                                                   ▼
                                         ┌────────────────────┐
                                         │       ESP32        │
                                         │  ─ L298N Motor PID │
                                         │  ─ MPU6050 IMU     │
                                         │  ─ HTTPS OTA       │
                                         └─────────┬──────────┘
                                                   │
                          /esp32/debug_status      │
                          /esp32/imu_debug         ▼
                                         ┌────────────────────┐
                                         │  multi_logger_node │
                                         │  video_logger_node │
                                         │       (옵션)        │
                                         └────────────────────┘
```

### 시뮬레이션 모드 (`/sim/...` 네임스페이스)

```
┌───────────────┐    /sim/image_raw      ┌────────────────────┐
│   Gazebo      │ ─────────────────────▶ │ sim_perception_node│
│ (lane_world)  │   (ros_gz_bridge)      └─────────┬──────────┘
│               │                                  │
│               │           /cmd_vel               ▼
│               │ ◀──────────────────────┬────────────────────┐
│               │                        │ sim_controller_node│
└───────┬───────┘                        └────────────────────┘
        │
        │ /odom (Gazebo → ROS)
        ▼
   (logger 등)
```

## 핵심 컴포넌트

### `camera_node`
USB 웹캠을 OpenCV(V4L2)로 열고 `/real/image_raw`로 publish.
- 640x480, MJPG, 약 30 FPS
- 캡처 실패 시 자동 재시도, 실패 누적 시 경고 로그

### `perception_node`
차선 + ArUco 마커 검출:
- 횡방향/방향/lookahead 오차 분리 발행 (제어 안정성)
- ArUco 마커 검출로 로봇 위치 + heading 추정
- waypoint 기반 경로 추적
- 디버그 이미지 2종 (시각화 + ROI binary)

### `sim_perception_node` / `sim_controller_node`
시뮬레이션 전용. ESP32 펌웨어 역할을 PC에서 대체:
- `sim_perception_node`: perception 결과를 시뮬레이션 좌표계로 변환
- `sim_controller_node`: PID 제어 → `/cmd_vel` 발행

### ESP32 펌웨어 (`main.c`)
- micro-ROS subscriber: 조향 명령, 탐색 명령 수신
- L298N 모터 PID 제어 (PWM 출력)
- MPU6050 IMU 읽기 → publish
- HTTPS OTA 클라이언트:
  - 부팅 시 UDP broadcast로 OTA 서버 자동 발견
  - `https://<server_ip>:8000/firmware.bin` 다운로드 후 펌웨어 교체

### `multi_logger_node`
ESP32 디버그/IMU 로그 + perception 상태를 20Hz로 CSV에 통합 저장.
- 출력: `~/lane_tracer_logs/csv/lane_minimal_*.csv`
- 정규식으로 ESP32 String 로그 파싱 → 컬럼별 저장

### `video_logger_node`
`/perception/debug_image` 또는 원본 카메라 영상을 MP4로 저장.
- 출력: `~/lane_tracer_logs/videos/perception_debug_*.mp4`
- 프레임마다 PC 시각 오버레이

## 통신 경로

| 구간                | 프로토콜       | 포트   | 비고                          |
|---------------------|----------------|--------|-------------------------------|
| PC ↔ ESP32 (제어)   | UDP            | 8888   | micro-ROS Agent               |
| PC → ESP32 (OTA)    | HTTPS          | 8000   | self-signed cert              |
| ESP32 → PC (디스커버리) | UDP broadcast | 19700  | "WHO_IS_OTA_SERVER" 요청      |
| PC ↔ Gazebo         | gRPC (내부)    | -      | `ros_gz_bridge` 가 처리        |
