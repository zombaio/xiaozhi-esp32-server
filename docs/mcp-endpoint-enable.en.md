# MCP Endpoint Deployment and Configuration Guide

This guide has three parts:
- 1) How to deploy the MCP Endpoint service
- 2) How to configure the MCP Endpoint for full-module deployments
- 3) How to configure the MCP Endpoint for single-module deployments

---

# 1. Deploying the MCP Endpoint service

## Step 1 — Download the source code

Open the project page in your browser: https://github.com/xinnan-tech/mcp-endpoint-server

Click the green **Code** button, then choose **Download ZIP**. After downloading, extract the archive (it may be named `mcp-endpoint-server-main`) and rename the folder to `mcp-endpoint-server`.

## Step 2 — Start the service

This project is simple; running it with Docker is recommended. If you prefer to run from source, see the dev README: https://github.com/xinnan-tech/mcp-endpoint-server/blob/main/README_dev.md

Docker steps:

```bash
# change to the project root
cd mcp-endpoint-server

# cleanup previous containers/images
docker compose -f docker-compose.yml down
docker stop mcp-endpoint-server || true
docker rm mcp-endpoint-server || true
docker rmi ghcr.nju.edu.cn/xinnan-tech/mcp-endpoint-server:latest || true

# start with docker compose
docker compose -f docker-compose.yml up -d
# view logs
docker logs -f mcp-endpoint-server
```

The container logs will show addresses like the following:

```
250705 INFO-===== Below are the Management Console / Single-module MCP endpoint addresses ====
250705 INFO-Management Console MCP config: http://172.22.0.2:8004/mcp_endpoint/health?key=abc
250705 INFO-Single-module MCP endpoint: ws://172.22.0.2:8004/mcp_endpoint/mcp/?token=def
250705 INFO-===== Use according to your deployment, do not share these addresses ======
```

Copy both addresses and keep them in a draft — you will need them later. Important: because the service runs in Docker, you must replace the internal container IP (e.g., `172.22.0.2`) with your host machine’s LAN IP or domain before using the addresses.

Example (if your host LAN IP is `192.168.1.25`):

Original addresses printed by the container:

```
Management Console MCP config: http://172.22.0.2:8004/mcp_endpoint/health?key=abc
Single-module MCP endpoint: ws://172.22.0.2:8004/mcp_endpoint/mcp/?token=def
```

Replace them with:

```
Management Console MCP config: http://192.168.1.25:8004/mcp_endpoint/health?key=abc
Single-module MCP endpoint: ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=def
```

After replacing, open the Management Console MCP config URL in a browser. A successful response looks like:

```
{"result":{"status":"success","connections":{"tool_connections":0,"robot_connections":0,"total_connections":0}},"error":null,"id":null,"jsonrpc":"2.0"}
```

Keep these two interface addresses safe — you will need them in the next sections.

---

# 2. Configure MCP Endpoint for full-module deployment

First enable the MCP Endpoint feature in the Management Console: go to **Parameter Dictionary** → **System Feature Configuration**, check **MCP Endpoint**, then click **Save Configuration**. In **Role Configuration**, click **Edit Functions** and you should see the `mcp endpoint` function available.

Using an administrator account, open **Parameter Management** in the Management Console and search for `server.mcp_endpoint`. By default this parameter is `null`.

Click **Edit**, paste the **Management Console MCP config** URL you obtained earlier into the parameter value, and save.

If saving succeeds, the Management Console can reach the MCP Endpoint and everything is configured. If saving fails, the console cannot reach the endpoint — check firewall rules or verify you used the correct LAN IP.

---

# 3. Configure MCP Endpoint for single-module deployment

If you run a single-module deployment, edit `data/.config.yaml` and add (or update) the `mcp_endpoint` entry.

Example configuration:

```yaml
server:
  websocket: ws://your-ip-or-domain:port/xiaozhi/v1/
  http_port: 8002
log:
  log_level: INFO

# ... other config ...

mcp_endpoint: ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=def
```

Paste the **Single-module MCP endpoint** URL you copied earlier into `mcp_endpoint`.

After configuring and starting the single-module server, you should see logs similar to:

```
250705[__main__]-INFO-Initialized component: vad success SileroVAD
250705[__main__]-INFO-Initialized component: asr success FunASRServer
250705[__main__]-INFO-OTA interface: http://192.168.1.25:8002/xiaozhi/ota/
250705[__main__]-INFO-Vision analyze interface: http://192.168.1.25:8002/mcp/vision/explain
250705[__main__]-INFO-mcp endpoint: ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
250705[__main__]-INFO-Websocket address: ws://192.168.1.25:8000/xiaozhi/v1/
250705[__main__]-INFO-======= Above addresses are WebSocket protocol addresses — do not open them in a browser =======
250705[__main__]-INFO-To test WebSocket, open test/test_page.html in Chrome
250705[__main__]-INFO-=============================================================
```

If you see a log line showing the `mcp endpoint` with your configured URL, the MCP Endpoint is configured successfully.

---

*End of guide.*