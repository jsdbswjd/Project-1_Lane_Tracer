# 영상 기반 AGV 주행 제어
### ROS 2 · ESP32 · micro-ROS 기반 차선 추종 로봇

**프로젝트 기간 | 2026.04–2026.05**

상부 카메라 영상에서 경로와 로봇 자세를 추정하고, ESP32에서 좌우 모터의 PWM을 제어하는 차선 추종 로봇 프로젝트입니다.

주행 오차를 **위치 편차·방향 차이·전방 목표점 오차**로 분리하여 각 요소에 대한 제어 반응을 조정했습니다. ROS 2 송신값과 ESP32 수신값, PWM·IMU 데이터를 기록해 신호 간 응답을 분석했으며, Gazebo에서는 같은 제어 구조로 주행 로직을 확인했습니다.

**주요 기술:** Python · OpenCV · ROS 2 Jazzy · micro-ROS · ESP32 · ESP-IDF · Gazebo Harmonic

### 기여 범위

- **본인:** `lane-tracer/` 개발 — 영상 처리, 주행 오차 계산, ESP32 PWM 제어, 통신·응답 분석 및 Gazebo 시뮬레이션 구성
- **팀원:** `dashboard/` 개발 — Flask 기반 웹 대시보드 및 ROS 2 브리지 구현

팀원이 개발한 대시보드를 이 저장소에 통합하여 주행 제어 코드와 함께 정리했습니다.

## 시연

### 실제 로봇 주행
상부 카메라 영상에서 경로 중심선과 로봇 자세를 추정하고, 전방 목표점을 따라 주행합니다.

<img width="320" height="240" alt="Video Project 5" src="https://github.com/user-attachments/assets/2883e013-6fb4-4c59-afb8-d4e226e6fb09" />


### Gazebo 시뮬레이션
영상 처리와 주행 제어 로직을 시뮬레이션 환경에서 확인했습니다.

<img width="320" height="240" alt="image" src="https://github.com/user-attachments/assets/7709f244-b5db-45e1-9fe1-e1ed5ba8cdce" />

- [최종 발표 자료 (PDF)](lane-tracer/docs/final-presentation.pdf)

## 담당 역할

| 영역 | 구현 내용 |
| --- | --- |
| 영상 처리 | ArUco 기반 로봇 자세 추정, 차체 영역 마스킹, 경로 중심선 추출 |
| 주행 제어 | 위치·방향·전방 목표점 오차 계산 및 좌우 모터 PWM 차등 보정 |
| 통신 및 분석 | ROS 2–ESP32 micro-ROS 연동, 송수신값·PWM·IMU 기록 및 비교 |
| 시뮬레이션 | Gazebo 환경 구성 및 주행 로직 확인 |

## 시스템 구성

| 구성 요소 | 역할 |
| --- | --- |
| 상부 카메라 · ROS 2 PC | 영상 처리, 경로 추출, 로봇 자세 및 주행 오차 계산 |
| micro-ROS Agent | Wi-Fi/UDP를 통한 ROS 2–ESP32 통신 |
| ESP32 · L298N | 수신한 주행 오차를 이용한 좌우 모터 PWM 제어 |
| MPU6050 | 주행 중 IMU 측정값 기록 |
| Gazebo | 영상 기반 주행 로직 확인 |
| 웹 대시보드 | ROS 2 경로 오차·IMU·ESP32 상태를 표시하는 모니터링 구성 |

ESP32 펌웨어의 HTTPS OTA 업데이트 기능도 포함합니다.

## 주요 구현

### 1. 경로 중심선 추출 및 전방 목표점 생성

- ArUco 마커로 로봇의 위치와 방향을 추정했습니다.
- 차체가 경로로 검출되지 않도록 로봇 영역을 마스킹했습니다.
- Skeletonization으로 주행 경로를 중심선 형태로 단순화했습니다.
- 로봇 전방에서 시작점을 선택하고, 거리·방향·이전 프레임과의 연속성을 고려해 전방 경로를 구성했습니다.
- 구성한 경로 위에서 일정 거리 앞의 lookahead 목표점을 계산했습니다.

### 2. 주행 오차 분리 및 PWM 제어

단일 오차만으로는 경로 복귀와 방향 정렬에 대한 반응을 개별적으로 조정하기 어려워, 제어 입력을 세 가지로 분리했습니다.

| 주행 오차 | 의미 |
| --- | --- |
| Lateral error | 경로에 대한 로봇의 수직 방향 위치 편차 |
| Heading error | 로봇 방향과 전방 경로 방향의 각도 차이 |
| Lookahead error | 로봇 방향과 전방 목표점을 바라보는 방향의 각도 차이 |

각 오차에 가중치를 적용해 보정량을 계산하고, 기준 PWM에 차등 반영했습니다.

```text
steer = Ky × lateral_error
      + Kθ × heading_error
      + Klook × lookahead_error

left_pwm  = base_pwm - steer
right_pwm = base_pwm + steer
```

ROS 2에서 주행 오차를 계산해 전달하고, ESP32 펌웨어에서 PWM 보정과 모터 구동을 수행합니다.

### 3. 송수신 데이터 및 주행 응답 분석

ROS 2 송신값, ESP32 수신값, PWM 보정량과 IMU 데이터를 기록해 단계별 신호를 비교했습니다.

| 분석 항목 | 관찰 결과 |
| --- | --- |
| ROS 2 송신값–ESP32 수신값 | 상관계수 0.99 이상 |
| 송수신 비교 신호의 시간차 | 약 2샘플 |
| PWM 차이–IMU 각속도의 시간차 | 약 0.30초 |

위 수치는 **기록 신호 사이에서 관찰한 시간차**이며, 통신 지연과 모터 응답 지연을 각각 독립적으로 측정한 결과는 아닙니다. 상관계수는 신호 변화 추세의 유사성을 나타내며, 절대값의 일치나 주행 정확도를 의미하지 않습니다.

### 4. Gazebo 시뮬레이션

실제 로봇과 같은 영상 처리·제어 구조를 구성해 주행 로직을 확인했습니다.

다만 카메라 영상 조건과 모터 모델에는 차이가 있습니다. 시뮬레이션에서는 ArUco 인식을 위해 영상 해상도를 높였으며, 실제 모터의 마찰과 PWM 데드존을 충분히 반영하지 못했습니다. 이에 따라 실제 주행과 시뮬레이션의 제어 파라미터를 구분했습니다.

## 검증 범위와 한계

- 엔코더가 없어 바퀴 속도의 추종 오차는 직접 평가하지 못했습니다.
- IMU는 주행 응답 분석에 사용했으며, 바퀴 속도 측정을 대체하지 않습니다.
- Gazebo는 주행 로직 확인에 사용했으며, 실제 구동계의 동특성을 재현한 모델은 아닙니다.

## 저장소 구성

| 경로 | 내용 |
| --- | --- |
| [`lane-tracer/ros2_ws/`](lane-tracer/ros2_ws/) | 영상 처리·주행 오차 계산·로깅·시뮬레이션 ROS 2 패키지 |
| [`lane-tracer/esp32_firmware/`](lane-tracer/esp32_firmware/) | micro-ROS 통신·PWM 제어·IMU·OTA 펌웨어 |
| [`lane-tracer/ota_server/`](lane-tracer/ota_server/) | 펌웨어 배포용 HTTPS 서버 |
| [`lane-tracer/docs/`](lane-tracer/docs/) | 아키텍처·토픽 명세·환경 구축 문서 |
| [`dashboard/`](dashboard/) | Flask 기반 웹 대시보드 및 ROS 2 브리지 |


## 설치 및 상세 문서

- [시스템 구성 및 빌드·실행 방법](lane-tracer/README.md)
- [아키텍처](lane-tracer/docs/architecture.md)
- [ROS 2 토픽 명세](lane-tracer/docs/topics.md)
- [ESP32 및 micro-ROS 환경 구축](lane-tracer/docs/esp32_microros_setup_guide.md)
- [ESP32 펌웨어 설정](lane-tracer/esp32_firmware/README.md)
- [OTA 서버 사용법](lane-tracer/ota_server/README.md)
- [웹 대시보드](dashboard/README.md)

## 라이선스

[Apache-2.0](lane-tracer/LICENSE)
