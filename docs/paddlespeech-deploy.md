# Integrate PaddleSpeech TTS with Xiaozhi

## Key notes
- Advantages: local, offline deployment and fast runtime.
- Limitation: as of 2025-09-25 the default PaddleSpeech models are Chinese-only and do not support English TTS. If the input contains English, no audio will be produced. To support both Chinese and English, you must train or obtain a multi-lingual model yourself.

## 1. Prerequisites
- OS: Windows / Linux / WSL2
- Python: 3.9+ (follow Paddle official guidance for exact versions)
- PaddlePaddle: use the official install instructions at https://www.paddlepaddle.org.cn/install
- Dependency management: conda or venv

## 2. Start the PaddleSpeech TTS server

### 1) Clone the official PaddleSpeech repository

```bash
git clone https://github.com/PaddlePaddle/PaddleSpeech.git
```

### 2) Create a virtual environment

```bash
conda create -n paddle_env python=3.10 -y
conda activate paddle_env
```

### 3) Install Paddle (follow official guidance)

Paddle installation differs by CPU/GPU and OS. Follow the official instructions for the appropriate packages and Python version:

https://www.paddlepaddle.org.cn/install

### 4) Change into the PaddleSpeech directory

```bash
cd PaddleSpeech
```

### 5) Install PaddleSpeech and dependencies

```bash
pip install pytest-runner -i https://pypi.tuna.tsinghua.edu.cn/simple

# Use one of the following commands to install Paddle and paddlespeech
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
pip install paddlespeech -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 6) Download a model automatically by running a quick TTS command

```bash
paddlespeech tts --input "你好，这是一次测试"
```

This command will automatically download the required models into `~/.paddlespeech/models`.

### 7) Edit `tts_online_application.yaml` to use WebSocket

File location example: `PaddleSpeech/demos/streaming_tts_server/conf/tts_online_application.yaml`

Open `tts_online_application.yaml` and set `protocol: websocket`.

### 8) Start the PaddleSpeech server

```bash
paddlespeech_server start --config_file ./demos/streaming_tts_server/conf/tts_online_application.yaml
# Official default start command (alternative):
paddlespeech_server start --config_file ./conf/tts_online_application.yaml
```

Start the service using the config path you edited. Successful startup emits logs similar to:

```
Prefix dict has been built successfully.
[2025-08-07 10:03:11,312] [   DEBUG] __init__.py:166 - Prefix dict has been built successfully.
INFO:     Started server process [2298]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8092 (Press CTRL+C to quit)
```

## 3. Configure Xiaozhi to use PaddleSpeech TTS

### 1) Provider code
- `main/xiaozhi-server/core/providers/tts/paddle_speech.py`

### 2) Configuration (example)
Edit `main/xiaozhi-server/data/.config.yaml` and add a single-module TTS configuration:

```yaml
selected_module:
  TTS: PaddleSpeechTTS
TTS:
  PaddleSpeechTTS:
      type: paddle_speech
      protocol: websocket 
      url: ws://127.0.0.1:8092/paddlespeech/tts/streaming  # PaddleSpeech WebSocket URL
      spk_id: 0        # Speaker ID (0 is usually the default)
      sample_rate: 24000  # Sample rate [websocket default 24000]
      speed: 1.0        # Speed multiplier (1.0 = normal)
      volume: 1.0       # Volume multiplier (1.0 = normal)
      save_path:        # Optional: path to save generated files
```

### 3) Start Xiaozhi and test

```bash
python app.py
```

Open `test/test_page.html` in a browser and try connecting/sending messages. Watch the PaddleSpeech server logs for incoming requests and timings.

Example PaddleSpeech logs when a WebSocket streaming request is received:

```
INFO:     127.0.0.1:44312 - "WebSocket /paddlespeech/tts/streaming" [accepted]
INFO:     connection open
[2025-08-07 11:16:33,355] [    INFO] - sentence: 哈哈，怎么突然找我聊天啦？
[2025-08-07 11:16:33,356] [    INFO] - The durations of audio is: 2.4625 s
[2025-08-07 11:16:33,356] [    INFO] - first response time: 0.1143045425415039 s
[2025-08-07 11:16:33,356] [    INFO] - final response time: 0.4777836799621582 s
[2025-08-07 11:16:33,356] [    INFO] - RTF: 0.19402382942625715
[2025-08-07 11:16:33,356] [    INFO] - Other info: front time: 0.06514096260070801 s, first am infer time: 0.008037090301513672 s, first voc infer time: 0.04112648963928223 s,
[2025-08-07 11:16:33,356] [    INFO] - Complete the synthesis of the audio streams
INFO:     connection closed
```

---

If you want, I can:
- Add this English file as `docs/paddlespeech-deploy.en.md` (done),
- Add a short link at the top of the original `docs/paddlespeech-deploy.md` pointing to the English version, or
- Replace the original with the English content.

Which option would you prefer?