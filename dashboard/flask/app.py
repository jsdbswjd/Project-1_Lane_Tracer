from flask import Flask, jsonify, render_template, request
import threading

app = Flask(__name__, template_folder="templates", static_folder="static")

state = {
    "imu": {"ax": 0.0, "ay": 0.0, "az": 0.0, "gx": 0.0, "gy": 0.0, "gz": 0.0},
    "path": {"lateral_error": 0.0, "heading_error": 0.0, "lookahead_error": 0.0},
    "esp_status": {"loop_rate": 0.0, "loop_dt": 0.0, "max_dt": 0.0, "rssi": 0, "wifi": 0, "ch": 0, "ip": "", "free_heap": 0, "min_heap": 0},
    "motor": {"left_pwm": 0, "right_pwm": 0, "steer": 0.0},
    "search_cmd": 0
}
state_lock = threading.Lock()

@app.route('/internal/imu', methods=['POST'])
def update_imu():
    with state_lock:
        state["imu"].update(request.json)
    return jsonify({"status": "ok"})

@app.route('/internal/path', methods=['POST'])
def update_path():
    with state_lock:
        state["path"].update(request.json)
    return jsonify({"status": "ok"})

@app.route('/internal/esp_status', methods=['POST'])
def update_esp_status():
    with state_lock:
        state["esp_status"].update(request.json)
    return jsonify({"status": "ok"})

@app.route('/internal/motor', methods=['POST'])
def update_motor():
    with state_lock:
        state["motor"].update(request.json)
    return jsonify({"status": "ok"})

@app.route('/internal/search_cmd', methods=['POST'])
def update_search_cmd():
    with state_lock:
        state["search_cmd"] = request.json.get("search_cmd", 0)
    return jsonify({"status": "ok"})

# script.js가 기대하는 flat 구조로 응답
@app.route('/api/robot_stats')
def get_robot_stats():
    with state_lock:
        s = state
        return jsonify({
            "lateral_error": s["path"]["lateral_error"],
            "heading_error":  s["path"]["heading_error"],
            "lookahead_error": s["path"]["lookahead_error"],
            "L_speed": round(s["motor"]["left_pwm"] / 255.0, 3),
            "R_speed": round(s["motor"]["right_pwm"] / 255.0, 3),
            "speed":   round((s["motor"]["left_pwm"] + s["motor"]["right_pwm"]) / 510.0, 3),
            "pwm_l":   s["motor"]["left_pwm"],
            "pwm_r":   s["motor"]["right_pwm"],
            "gyro_x":  s["imu"]["gx"],
            "heading": 0.0,
            "distance": 0.0,
            "pulse": 0,
            "obstacle": "안전",
            "motor": "가동중 🟢",
            "search_cmd": s["search_cmd"],
            "esp": {
                "loop_rate": s["esp_status"]["loop_rate"],
                "loop_dt":   s["esp_status"]["loop_dt"],
                "max_dt":    s["esp_status"]["max_dt"],
                "wifi":      s["esp_status"]["wifi"],
                "rssi":      s["esp_status"]["rssi"],
                "ch":        s["esp_status"]["ch"],
                "ip":        s["esp_status"]["ip"],
                "free_heap": s["esp_status"]["free_heap"],
                "min_heap":  s["esp_status"]["min_heap"]
            },
            "transform": {
                "theta_deg": 0.0, "cx": 0, "cy": 0,
                "s": 4.27, "xc": 0.0, "yc": 0.0
            },
            "imu": s["imu"]
        })

@app.route('/api/weather')
def get_weather():
    return jsonify({"status": "ok", "summary": "맑음", "temp": "--°C", "humidity": "--%"})

@app.route('/api/news')
def get_news():
    return jsonify([])

@app.route('/api/system_logs')
def get_system_logs():
    return jsonify([])

@app.route('/api/cmd', methods=['POST'])
def send_cmd():
    data = request.json
    direction = data.get('direction', 'S')
    with state_lock:
        state['remote_cmd'] = direction
    return jsonify({"status": "ok", "cmd": direction})

@app.route('/update_position', methods=['POST'])
def update_position():
    return jsonify({"status": "ok"})

@app.route('/api/remote_cmd')
def get_remote_cmd():
    with state_lock:
        return jsonify({"cmd": state.get('remote_cmd', 'S')})

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/')
def dashboard():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
