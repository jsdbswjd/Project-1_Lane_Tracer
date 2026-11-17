import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String, Int32
import requests
import re
import time
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

FLASK_URL = "http://localhost:5000"

class ROS2Bridge(Node):
    def __init__(self):
        super().__init__('ros2_bridge')

        best_effort_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.create_subscription(String, '/esp32/imu_debug', self.imu_cb, best_effort_qos)
        self.create_subscription(String, '/esp32/status', self.status_cb, best_effort_qos)
        self.create_subscription(String, '/esp32/debug_status', self.debug_cb, best_effort_qos)
        self.create_subscription(Float32, '/real/path/lateral_error', self.lateral_cb, 10)
        self.create_subscription(Float32, '/real/path/heading_error', self.heading_cb, 10)
        self.create_subscription(Float32, '/real/path/lookahead_error', self.lookahead_cb, 10)
        self.remote_cmd_pub = self.create_publisher(String, '/real/remote/cmd', 10)

        self.path_data = {"lateral_error": 0.0, "heading_error": 0.0, "lookahead_error": 0.0}
        self._last_path_send = 0
        self.get_logger().info("ROS2 Bridge started")
        
        self._last_remote_cmd = 'S'
        # self.create_timer(0.1, self.poll_remote_cmd)  # Monitoring only
        
    def poll_remote_cmd(self):
        try:
            res = requests.get(f"{FLASK_URL}/api/remote_cmd", timeout=0.2)
            cmd = res.json().get('cmd', 'S')
            self._last_remote_cmd = cmd
            msg = String()
            msg.data = cmd
            self.remote_cmd_pub.publish(msg)
        except Exception:
            pass
        
    def imu_cb(self, msg):
        try:
            d = msg.data
            data = {
                "ax": float(re.search(r'Ax:([-\d.]+)', d).group(1)),
                "ay": float(re.search(r'Ay:([-\d.]+)', d).group(1)),
                "az": float(re.search(r'Az:([-\d.]+)', d).group(1)),
                "gx": float(re.search(r'Gx:([-\d.]+)', d).group(1)),
                "gy": float(re.search(r'Gy:([-\d.]+)', d).group(1)),
                "gz": float(re.search(r'Gz:([-\d.]+)', d).group(1)),
            }
            requests.post(f"{FLASK_URL}/internal/imu", json=data, timeout=0.2)
        except Exception as e:
            self.get_logger().warn(f"imu_cb error: {e}")

    def status_cb(self, msg):
        try:
            d = msg.data
            data = {}
            for key, pattern in [
                ("loop_rate", r'LoopRate:([-\d.]+)'),
                ("loop_dt",   r'LoopDt:([-\d.]+)'),
                ("max_dt",    r'MaxLoopDt:([-\d.]+)'),
                ("wifi",      r'WiFi:(\d+)'),
                ("rssi",      r'RSSI:([-\d.]+)'),
                ("ch",        r'CH:(\d+)'),
                ("ip",        r'IP:([\d.]+)'),
                ("free_heap", r'FreeHeap:(\d+)'),
                ("min_heap",  r'MinF[^:]*:(\d+)'),
            ]:
                m = re.search(pattern, d)
                if m:
                    data[key] = float(m.group(1)) if key not in ('ip',) else m.group(1)
            if data:
                requests.post(f"{FLASK_URL}/internal/esp_status", json=data, timeout=0.2)
        except Exception as e:
            self.get_logger().warn(f"status_cb error: {e}")

    def lateral_cb(self, msg):
        self.path_data["lateral_error"] = msg.data
        self._send_path()

    def heading_cb(self, msg):
        self.path_data["heading_error"] = msg.data
        self._send_path()

    def lookahead_cb(self, msg):
        self.path_data["lookahead_error"] = msg.data
        self._send_path()

    def _send_path(self):
        now = time.time()
        if now - self._last_path_send < 0.1:
            return
        self._last_path_send = now
        try:
            requests.post(f"{FLASK_URL}/internal/path", json=self.path_data, timeout=0.2)
        except Exception as e:
            self.get_logger().warn(f"path send error: {e}")

    def debug_cb(self, msg):
        try:
            d = msg.data
            data = {}
            for key, pattern in [
                ("left_pwm",  r'PL:([-\d.]+)'),
                ("right_pwm", r'PR:([-\d.]+)'),
                ("steer",     r'ST:([-\d.]+)'),
            ]:
                m = re.search(pattern, d)
                if m:
                    data[key] = float(m.group(1))
            if data:
                requests.post(f"{FLASK_URL}/internal/motor", json=data, timeout=0.2)
        except Exception as e:
            self.get_logger().warn(f"debug_cb error: {e}")

def main():
    rclpy.init()
    node = ROS2Bridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
