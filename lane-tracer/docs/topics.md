# ROS 2 Topic 명세

이 프로젝트는 토픽을 `/real/...`(실제 하드웨어)과 `/sim/...`(Gazebo 시뮬레이션)으로
네임스페이스를 분리합니다. 같은 perception 로직이 두 모드에서 독립적으로 돌 수 있어요.

## 실제 하드웨어 (`/real/...`)

### Camera → Perception

| Topic                              | Type                   | Pub               | 설명                          |
|------------------------------------|------------------------|-------------------|-------------------------------|
| `/real/image_raw`                  | `sensor_msgs/Image`    | camera_node       | USB 웹캠 원본 (640x480 BGR)   |

### Perception → 제어 / 디버그

| Topic                                  | Type                   | 설명                            |
|----------------------------------------|------------------------|---------------------------------|
| `/real/path/lateral_error`             | `std_msgs/Float32`     | 횡방향 오차                     |
| `/real/path/heading_error`             | `std_msgs/Float32`     | 방향 오차                       |
| `/real/path/lookahead_error`           | `std_msgs/Float32`     | lookahead 지점 오차             |
| `/real/perception/debug_image`         | `sensor_msgs/Image`    | 시각화 디버그 이미지            |
| `/real/perception/roi_binary_image`    | `sensor_msgs/Image`    | skeleton + waypoint 디버그      |
| `/real/perception/search_cmd`          | `std_msgs/Int32`       | 차선 탐색 명령                  |
| `/real/perception/log_status`          | `std_msgs/String`      | ArUco/waypoint/path 통합 상태   |

### ESP32 → PC (micro-ROS)

| Topic                       | Type                 | 설명                                                |
|-----------------------------|----------------------|-----------------------------------------------------|
| `/esp32/debug_status`       | `std_msgs/String`    | `CamErr:.. Steer:.. L:.. R:.. Valid:.. Search:.. Lost:..` |
| `/esp32/imu_debug`          | `std_msgs/String`    | `Gz:..` 등 MPU6050 IMU 데이터                       |

### PC → ESP32 (micro-ROS)

| Topic                       | Type                 | 설명                            |
|-----------------------------|----------------------|---------------------------------|
| `/target_heading_error`     | `std_msgs/Float32`   | 조향 에러                       |
| `/perception/search_cmd`    | `std_msgs/Int32`     | 차선 탐색 명령 (0/1)            |

> ESP32 펌웨어는 이 두 토픽을 subscribe 합니다. perception_node가 발행하는 `/real/...`
> 토픽을 그대로 쓰지 않는 이유는, 펌웨어 측 토픽 이름을 단순하게 유지하기 위함입니다.
> 토픽 매핑은 launch 파일에서 `remap`으로 처리됩니다.

## Gazebo 시뮬레이션 (`/sim/...`)

`/real/...`와 동일한 토픽 구조의 미러링:

| Topic                                  | Type                   |
|----------------------------------------|------------------------|
| `/sim/image_raw`                       | `sensor_msgs/Image`    |
| `/sim/path/lateral_error`              | `std_msgs/Float32`     |
| `/sim/path/heading_error`              | `std_msgs/Float32`     |
| `/sim/path/lookahead_error`            | `std_msgs/Float32`     |
| `/sim/perception/debug_image`          | `sensor_msgs/Image`    |
| `/sim/perception/roi_binary_image`     | `sensor_msgs/Image`    |
| `/sim/perception/search_cmd`           | `std_msgs/Int32`       |
| `/sim/perception/log_status`           | `std_msgs/String`      |

### Gazebo Bridge

`ros_gz_bridge` (`gazebo_lane.launch.py` 참고)

| Topic         | Direction       | Type                                    |
|---------------|-----------------|-----------------------------------------|
| `/cmd_vel`    | ROS → Gazebo    | `geometry_msgs/Twist` ↔ `gz.msgs.Twist` |
| `/odom`       | Gazebo → ROS    | `nav_msgs/Odometry` ↔ `gz.msgs.Odometry`|
| `/image_raw`  | Gazebo → ROS    | `sensor_msgs/Image` ↔ `gz.msgs.Image`   |
