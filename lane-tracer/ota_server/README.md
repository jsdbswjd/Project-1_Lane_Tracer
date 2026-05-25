# OTA Server

ESP32용 HTTPS OTA 서버.

두 가지 기능을 동시에 제공합니다:
1. **UDP 디스커버리 (포트 19700)**: ESP32가 `WHO_IS_OTA_SERVER` broadcast를 보내면
   서버 IP로 응답합니다. ESP32에 IP를 하드코딩할 필요가 없어요.
2. **HTTPS 파일 서버 (포트 8000)**: 현재 디렉토리의 파일을 HTTPS로 제공합니다.
   ESP32는 `https://<server_ip>:8000/firmware.bin`에서 새 펌웨어를 받아갑니다.

## 설치

```bash
# Python 3.8+ 만 있으면 됨 (외부 패키지 없음)
pip install -r requirements.txt
```

## 인증서 생성 (최초 1회)

```bash
openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout server.key -out server.crt -days 365 \
    -subj "/CN=lane-tracer-ota"
```

> ⚠️ `server.key`, `server.crt`는 `.gitignore`에 포함되어 있어 Git에 올라가지 않습니다.

## 실행

```bash
python3 https_server.py
```

새 펌웨어를 배포하려면 `firmware.bin`을 이 디렉토리에 두세요:

```bash
cp ../esp32_firmware/build/lane_tracer_firmware.bin ./firmware.bin
```

## 방화벽

다음 포트를 인바운드로 허용해야 합니다:

| 포트  | 프로토콜 | 용도              |
|-------|----------|-------------------|
| 19700 | UDP      | 서버 디스커버리   |
| 8000  | TCP      | HTTPS 펌웨어 배포 |
