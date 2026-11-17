FROM ros:jazzy
RUN apt-get update && apt-get install -y python3-pip && \
    pip3 install requests --break-system-packages
COPY ros2_bridge.py /ros2_ws/ros2_bridge.py
