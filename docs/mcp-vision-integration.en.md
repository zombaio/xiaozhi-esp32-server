# Vision Model Guide

This guide explains how to enable and use the visual model (MCP Vision) in two cases:
- Single-module deployment (run `xiaozhi-server` standalone)
- Full-module deployment (docker-compose / all modules)

Before enabling the vision model, prepare the following:
- A device with a camera and a firmware that supports camera calls (for example, the Lichuang ESP32-S3 dev board).
- Device firmware version **1.6.6** or newer.
- A working basic conversation flow (the server and core modules are running).

## Enabling MCP Vision on a single-module `xiaozhi-server` instance

### Step 1 — Network checks

The vision service exposes an HTTP endpoint on port **8003** by default. Ensure the port is reachable:
- If you run with Docker, make sure `8003` is mapped in `docker-compose.yml`.
- If you run from source, ensure the firewall allows inbound connections on `8003`.

### Step 2 — Choose a vision-capable LLM (VLLM)

Open `data/.config.yaml` and set `selected_module.VLLM` to a VLLM that supports vision. The project supports OpenAI-compatible vision models; for example `ChatGLMVLLM`.

```yaml
selected_module:
  VAD: ..
  ASR: ..
  LLM: ..
  VLLM: ChatGLMVLLM
  TTS: ..
  Memory: ..
  Intent: ..
```

If you choose `ChatGLMVLLM`, obtain an API key from https://bigmodel.cn/usercenter/proj-mgmt/apikeys and set the key in your config:

```yaml
VLLM:
  ChatGLMVLLM:
    api_key: YOUR_API_KEY
```

### Step 3 — Start (or restart) the server

From source:

```bash
python app.py
```

With Docker:

```bash
docker restart xiaozhi-esp32-server
```

After startup you should see log lines like:

```
2025-06-01 **** - OTA interface: http://192.168.4.7:8003/xiaozhi/ota/
2025-06-01 **** - Vision explain interface: http://192.168.4.7:8003/mcp/vision/explain
2025-06-01 **** - Websocket address: ws://192.168.4.7:8000/xiaozhi/v1/
2025-06-01 **** - ======= Above addresses are WebSocket addresses — do not open them in a browser =======
2025-06-01 **** - To test WebSocket, open test/test_page.html in Chrome
2025-06-01 **** - =============================================================
```

Open the **Vision explain interface** URL in a browser or use curl:

```bash
curl -i http://YOUR_HOST:8003/mcp/vision/explain
```

A healthy response looks like:

```
MCP Vision interface is running; Vision explain interface is: http://xxxx:8003/mcp/vision/explain
```

Important: if you run in Docker or deploy on a public host, set the public-accessible `vision_explain` URL in `data/.config.yaml` so devices can reach it:

```yaml
server:
  vision_explain: http://YOUR_PUBLIC_IP_OR_DOMAIN:8003/mcp/vision/explain
```

If your public IP is `111.111.111.111`, configure:

```yaml
server:
  vision_explain: http://111.111.111.111:8003/mcp/vision/explain
```

After confirming the MCP Vision endpoint responds, continue to the next step.

### Step 4 — Wake the device and request vision output

Speak to the device: “Please open the camera and tell me what you see.”

Watch the `xiaozhi-server` logs for errors and confirm the visual analysis results are returned.

---

## Enabling MCP Vision in full-module deployments

### Step 1 — Network checks

As with single-module deployments, ensure port **8003** is exposed and reachable:
- For docker-compose deployments, verify `docker-compose_all.yml` maps port `8003`.
- For source runs, confirm the firewall allows port `8003`.

### Step 2 — Confirm configuration structure

Open `data/.config.yaml` and ensure its structure matches `data/config_from_api.yaml`. Fill any missing fields or sections.

### Step 3 — Configure the vision model API key

Obtain an API key from https://bigmodel.cn/usercenter/proj-mgmt/apikeys (or other supported provider).

In the Management Console go to **Model Configuration → Vision LLM**. Find the `VLLM_ChatGLMVLLM` entry, click **Edit**, enter the API key in the **API Key** field, and save.

Then open the target agent’s **Configure Roles** dialog and confirm the **Vision LLM (VLLM)** selection uses the model you configured. Save.

### Step 4 — Start (or restart) the server

From source:

```bash
python app.py
```

With Docker:

```bash
docker restart xiaozhi-esp32-server
```

After startup check the relevant logs and verify the Vision explain endpoint responds (see Step 3 in the single-module section). Make sure `server.vision_explain` points to a reachable public URL if devices are expected to access it.

### Step 5 — Wake the device and request vision output

Say: “Please open the camera and tell me what you see.”

Monitor the `xiaozhi-server` logs and confirm there are no errors and an explanation is produced.

---

*This is an English translation of `docs/mcp-vision-integration.md`. The original file remains unchanged.*