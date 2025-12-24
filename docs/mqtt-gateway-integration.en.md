# MQTT Gateway Deployment Guide

The `xiaozhi-esp32-server` project can be combined with the modified open-source [xiaozhi-mqtt-gateway](https://github.com/78/xiaozhi-mqtt-gateway) project to enable MQTT + UDP connectivity for XiaoZhi hardware. This guide has three parts — choose the part that matches your deployment type (full-module or single-module):

- Part 1: Deploy the MQTT Gateway
- Part 2: Full-module setup to enable device MQTT + UDP connectivity
- Part 3: Single-module setup to enable device MQTT + UDP connectivity

---

## Preparation

Prepare the server WebSocket address for `mqtt-websocket`. On top of your existing websocket URL, append `?from=mqtt_gateway` to get the MQTT-WebSocket address.

1) For source (local) deployments, the `mqtt-websocket` address is:
```
ws://127.0.0.1:8000/xiaozhi/v1/?from=mqtt_gateway
```

2) For Docker deployments, use your host LAN IP:
```
ws://<your-host-lan-ip>:8000/xiaozhi/v1/?from=mqtt_gateway
```

### Important note

Ensure the following ports are open on your server: **1883**, **8884**, and **8007**. Port **8884** must use UDP; the others are TCP.

---

## Part 1 — Deploy the MQTT Gateway

1. Clone the modified `xiaozhi-mqtt-gateway` project:

```bash
git clone https://ghfast.top/https://github.com/xinnan-tech/xiaozhi-mqtt-gateway.git
cd xiaozhi-mqtt-gateway
```

2. Install dependencies:

```bash
npm install
npm install -g pm2
```

3. Copy the example config:

```bash
cp config/mqtt.json.example config/mqtt.json
```

4. Edit `config/mqtt.json` and replace `chat_servers` with your `mqtt-websocket` address from the preparation step. Example (local source deployment):

```json
{
    "production": {
        "chat_servers": [
            "ws://127.0.0.1:8000/xiaozhi/v1/?from=mqtt_gateway"
        ]
    },
    "debug": false,
    "max_mqtt_payload_size": 8192,
    "mcp_client": { ... }
}
```

5. Create a `.env` file in the project root and set these environment variables:

```
PUBLIC_IP=your-ip         # public IP or domain
MQTT_PORT=1883            # MQTT server port
UDP_PORT=8884             # UDP server port
API_PORT=8007             # management API port
MQTT_SIGNATURE_KEY=test   # MQTT authentication signature key
SERVER_SECRET=Te1st12134  # server secret; keep it in sync with server.secret or server.auth_key
```

- Make sure `PUBLIC_IP` matches your public IP or domain.
- Choose a strong `MQTT_SIGNATURE_KEY` (8+ chars, mixed case recommended).
- `SERVER_SECRET` is used for websocket authentication.

Notes:
- If the Management Console has `server.auth.enabled` set to `true`, then `SERVER_SECRET` must match the console's `server.secret`.
- If you use single-module deployment with `server.auth.enabled` set to `true` in your config, `SERVER_SECRET` must match `server.auth_key`.

6. Start the MQTT Gateway:

```bash
# start
pm2 start ecosystem.config.js
# view logs
pm2 logs xz-mqtt
```

Successful startup shows logs like:

```
0|xz-mqtt  | 2025-09-11T12:14:48: MQTT server listening on port 1883
0|xz-mqtt  | 2025-09-11T12:14:48: UDP server listening on x.x.x.x:8884
```

To restart:
```
pm2 restart xz-mqtt
```

---

## Part 2 — Full-module deployment: enable MQTT + UDP for hardware

Ensure your Management Console version is **0.7.7** or newer (check the version at the bottom of the console home page); upgrade if necessary.

1. In the Management Console, go to **Parameter Management** and edit `server.mqtt_gateway`. Set it to `PUBLIC_IP:MQTT_PORT` (example: `192.168.0.7:1883`).

2. Edit `server.mqtt_signature_key` and set it to your `MQTT_SIGNATURE_KEY`.

3. Edit `server.udp_gateway` and set it to `PUBLIC_IP:UDP_PORT` (example: `192.168.0.7:8884`).

4. Edit `server.mqtt_manager_api` and set it to `PUBLIC_IP:API_PORT` (example: `192.168.0.7:8007`).

After applying the above, verify the OTA service will deliver MQTT configuration. Replace `http://localhost:8002/xiaozhi/ota/` with your OTA URL:

```bash
curl 'http://localhost:8002/xiaozhi/ota/' \
  -H 'Content-Type: application/json' \
  -H 'Client-Id: <client-id>' \
  -H 'Device-Id: 11:22:33:44:55:66' \
  --data-raw '{"application":{"version":"1.0.1","elf_sha256":"1"},"board":{"mac":"11:22:33:44:55:66"}}'
```

If the response includes `mqtt` configuration, the OTA delivery worked. Example excerpt:

```json
"mqtt":{"endpoint":"192.168.0.7:1883","client_id":"...","username":"...","password":"...","publish_topic":"device-server","subscribe_topic":"devices/p2p/11_22_33_44_55_66"}
```

Note: MQTT config is delivered via OTA — ensure your devices can access the OTA URL and reboot/wake them to receive the config.

Monitor the gateway logs for connections:

```
pm2 logs xz-mqtt
```

---

## Part 3 — Single-module deployment: enable MQTT + UDP for hardware

Edit `data/.config.yaml` and under `server` set the following values to match your `.env`:

```
mqtt_gateway: 192.168.0.7:1883
mqtt_signature_key: <your-mqtt-signature-key>
udp_gateway: 192.168.0.7:8884
```

Verify OTA delivery using the curl command (replace OTA URL and Device-Id accordingly). If the returned JSON contains `mqtt` config, the device will receive it after reboot/wake.

After device wake, check the MQTT gateway logs for successful connection messages:

```
pm2 logs xz-mqtt
```

---

*This is an English translation of `docs/mqtt-gateway-integration.md`. The original file has been preserved.*