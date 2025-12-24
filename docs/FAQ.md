# Frequently Asked Questions ❓

### 1) Why is my speech sometimes recognized as Korean, Japanese, or English? 🇰🇷🇯🇵🇬🇧

Suggestion: Check that `models/SenseVoiceSmall` contains `model.pt`. If it is missing, download the model files — see the "Model files" section in `Deployment.md`.

### 2) Why do I see "TTS task error: file not found"? 📁

Suggestion: Make sure `libopus` and `ffmpeg` are installed correctly (we recommend using `conda`). To install:

```bash
conda install -c conda-forge libopus
conda install -c conda-forge ffmpeg
```

### 3) TTS frequently fails or times out ⏰

Suggestion: If `EdgeTTS` often fails, check whether you are using a network proxy or VPN — try disabling it. If you are using Volcengine Doubao TTS and see frequent failures, consider the paid tier because the free/test tier supports only 2 concurrent sessions.

### 4) Wi‑Fi can connect to my self-hosted server, but 4G cannot 🔐

Cause: Some device firmware requires a secure (HTTPS) connection when operating over 4G.

Solutions (choose one):

1. Modify the device firmware — see this walkthrough video: https://www.bilibili.com/video/BV18MfTYoE85
2. Configure Nginx with an SSL certificate — see the tutorial: https://icnt94i5ctj4.feishu.cn/docx/GnYOdMNJOoRCljx1ctecsj9cnRe

### 5) How can I improve Xiaozhi's response speed? ⚡

The project defaults to a low-cost setup so it is easier to get started. Once it runs correctly, you can optimize for speed by swapping components. Since v0.5.2 the project supports streaming configurations, which can reduce response latency by ~2.5s compared to previous setups.

| Component | Free beginner setup | Streaming / Faster option |
|:---:|:---|:---|
| ASR (speech recognition) | FunASR (local) | 👍 XunfeiStreamASR (streaming)
| LLM (large language model) | glm-4-flash | 👍 qwen-flash
| VLLM (vision LLM) | glm-4v-flash | 👍 qwen2.5-vl-3b-instructh
| TTS (text-to-speech) | ✅ LinkeraiTTS (streaming) | 👍 HuoshanDoubleStreamTTS (streaming)
| Intent (intent detection) | function_call | function_call
| Memory (memory subsystem) | mem_local_short | mem_local_short

If you care about per-component latency, see the Xiaozhi performance reports and reproduce tests in your environment: https://github.com/xinnan-tech/xiaozhi-performance-research

### 6) I speak slowly and Xiaozhi often interrupts me 🗣️

Suggestion: Increase `min_silence_duration_ms` in your config (e.g., set it to `1000`):

```yaml
VAD:
  SileroVAD:
    threshold: 0.5
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 700  # increase this if speakers pause for a long time
```

### 7) Deployment guides
1. [Minimal deployment](./Deployment.md)
2. [Full-module deployment](./Deployment_all.md)
3. [Deploy MQTT gateway (enable MQTT+UDP)](./mqtt-gateway-integration.md)
4. [Auto-pull, build and start (CI)](./dev-ops-integration.md)
5. [Integrating with Nginx (discussion / issue)](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791)

### 9) Firmware build guides
1. [How to build Xiaozhi firmware](./firmware-build.md)
2. [How to change the OTA address in pre-built firmware](./firmware-setting.md)

### 10) Integration & extension guides
1. [Enable phone-number registration for the console](./ali-sms-integration.md)
2. [Integrate HomeAssistant for smart home control](./homeassistant-integration.md)
3. [Enable vision models for photo recognition](./mcp-vision-integration.md)
4. [Deploy an MCP endpoint](./mcp-endpoint-enable.md)
5. [How to connect to an MCP endpoint](./mcp-endpoint-integration.md)
6. [How to get device info via MCP methods](./mcp-get-device-info.md)
7. [Enable voiceprint (speaker recognition)](./voiceprint-integration.md)
8. [News plugin source configuration guide](./newsnow_plugin_config.md)
9. [Knowledge-base (ragflow) integration guide](./ragflow-integration.md)
10. [How to deploy context providers](./context-provider-integration.md)

### 11) Voice cloning & local TTS guides
1. [How to clone a voice in the console](./huoshan-streamTTS-voice-cloning.md)
2. [How to deploy index-tts local speech](./index-stream-integration.md)
3. [How to deploy fish-speech local TTS](./fish-speech-integration.md)
4. [How to deploy PaddleSpeech local TTS](./paddlespeech-deploy.md)

### 12) Performance testing
1. [Component speed testing guide](./performance_tester.md)
2. [Public test results (updated periodically)](https://github.com/xinnan-tech/xiaozhi-performance-research)

### 13) More questions / contact 💬

Please file an issue at: https://github.com/xinnan-tech/xiaozhi-esp32-server/issues
