# Lane Tracer

ROS 2 Jazzy와 ESP32 micro-ROS를 연동한 차선 추종 RC 로봇 프로젝트입니다.
카메라 영상에서 계산한 차선 방향 오차를 Wi-Fi/UDP로 ESP32에 전달해
모터를 제어합니다. 실물 주행과 Gazebo 시뮬레이션을 지원합니다.

- [시스템 구성 및 실행 방법](lane-tracer/README.md)
- [아키텍처](lane-tracer/docs/architecture.md)
- [ESP32 펌웨어 설정](lane-tracer/esp32_firmware/README.md)
