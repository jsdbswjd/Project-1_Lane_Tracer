# Lane Tracer 웹 대시보드

ROS 2에서 수신한 차선 추종 오차, IMU 측정값, ESP32 상태를 웹에서 확인할 수 있습니다.

## 개발 및 통합

Flask 대시보드와 ROS 2 브리지는 팀원 [@futurexst](https://github.com/futurexst)가 개발했습니다. 차선 추종 시스템과 함께 사용할 수 있도록 이 저장소의 `dashboard/`에 통합했습니다.

## 실행

Docker Compose가 설치된 환경에서 저장소 루트 기준으로 실행합니다.

```bash
docker compose -f dashboard/docker-compose.yml up -d --build
```

브라우저에서 [http://localhost:5000](http://localhost:5000)을 엽니다.

Compose는 micro-ROS Agent를 UDP 8888에서 함께 실행합니다. 기존 Agent를 사용 중이라면 서비스 이름 `ros2 flask`를 실행 명령 끝에 붙여 대시보드와 브리지만 시작합니다.

현재 구성은 **모니터링 모드**이며, 웹에서 ROS 2로 원격 주행 명령을 발행하는 기능은 비활성화되어 있습니다.

- 참고: [팀원의 ROS 2 Docker 운영 환경 및 관제 웹](https://github.com/futurexst/robot_ws)
