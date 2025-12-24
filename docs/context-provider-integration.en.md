# Context Providers — Usage Guide

## Overview

A “context provider” supplies external data to the system prompt used by Xiaozhi.

When Xiaozhi wakes up, the context provider fetches external data and dynamically injects it into the large-model System Prompt so the model can be aware of the current state of some real-world things.

Context providers are different from MCP and Memory:
- Context providers are authoritative, real‑time data sources that must be visible to Xiaozhi at wake time.
- Memory (Mem) records past conversation history.
- MCP (function call) is used to invoke capabilities or external logic on demand.

With context providers, Xiaozhi can be aware at wake time of items such as:
- Health sensor status (temperature, blood pressure, SpO2, etc.)
- Real-time business metrics (server load, pending tasks, stock quotes)
- Any textual data reachable via an HTTP API

Note: Context providers are meant to provide state at wake time. If you need continuous or post-wake updates, combine context providers with MCP tool calls for live refresh.

## How it works

1. Configure one or more HTTP API endpoints as context providers.
2. When the system builds a prompt and finds the `{{ dynamic_context }}` placeholder, it issues GET requests to all configured APIs.
3. The system formats API responses as a Markdown list and replaces `{{ dynamic_context }}` with the formatted content.

## API contract

To be consumable by Xiaozhi, your API should follow these rules:

- HTTP method: GET
- Request headers: the system automatically adds a `device-id` header.
- Response format: JSON with `code` and `data` fields.

### Response examples

**Case 1 — Key/Value object (dictionary)**

JSON response:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "Living room temperature": "26℃",
    "Living room humidity": "45%",
    "Front door": "Closed"
  }
}
```
Injection result:
```markdown
<context>
- **Living room temperature:** 26℃
- **Living room humidity:** 45%
- **Front door:** Closed
</context>
```

**Case 2 — List**

JSON response:
```json
{
  "code": 0,
  "data": [
    "You have 10 pending tasks",
    "Current vehicle speed: 100 km/h"
  ]
}
```
Injection result:
```markdown
<context>
- You have 10 pending tasks
- Current vehicle speed: 100 km/h
</context>
```

## Configuration guide

### Method 1 — Configure via Admin Console (full-stack deployments)

1. Log in to the Admin Console and go to **Role Configuration**.
2. Find the **Context Providers** area and click **Edit Sources**.
3. Click **Add**, and enter your API URL.
4. If the API needs authentication, add `Authorization` or other headers in the **Request Headers** section.
5. Save the configuration.

### Method 2 — Configure via `.config.yaml` (single‑module deployments)

Edit `xiaozhi-server/data/.config.yaml` and add a `context_providers` block, e.g.:

```yaml
# Context providers configuration
context_providers:
  - url: "http://api.example.com/data"
    headers:
      Authorization: "Bearer your-token"
  - url: "http://another-api.com/data"
```

## Enabling the feature

By default, the prompt template file (`data/.agent-base-prompt.txt`) already contains the `{{ dynamic_context }}` placeholder, so you usually do not need to edit the template.

Example template snippet:

```markdown
<context>
[IMPORTANT: The following information is provided in real-time — use directly without calling tools.]
- **Device ID:** {{device_id}}
- **Current time:** {{current_time}}
...
{{ dynamic_context }}
</context>
```

If you do not want to use context providers, either do not configure any providers or remove the `{{ dynamic_context }}` placeholder from the prompt template.

## Appendix: Mock API server for testing

To help development and testing, here is a simple Python mock server you can run locally.

**mock_api_server.py**

```python
import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

# Port to listen on
PORT = 8081

class MockRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse path and query
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        response_data = {}
        status_code = 200

        print(f"Received request: {path}, query: {query}")

        # Case 1: Health data (dictionary)
        # Path: /health
        # device_id is read from the Header
        if path == "/health":
            device_id = self.headers.get("device-id", "unknown_device")
            print(f"device_id: {device_id}")
            response_data = {
                "code": 0,
                "msg": "success",
                "data": {
                    "Test device ID": device_id,
                    "Heart rate": "80 bpm",
                    "Blood pressure": "120/80 mmHg",
                    "Status": "Good"
                }
            }

        # Case 2: News list (returns an array)
        elif path == "/news/list":
            response_data = {
                "code": 0,
                "msg": "success",
                "data": [
                    "Headline: Python 3.14 released",
                    "Tech: AI assistants changing lives",
                    "Local: Heavy rain tomorrow — bring an umbrella"
                ]
            }

        # Case 3: Weather summary (string)
        elif path == "/weather/simple":
            response_data = {
                "code": 0,
                "msg": "success",
                "data": "Sunny turning cloudy today, 20-25°C, good air quality — suitable for going out."
            }

        # Case 4: Device info via query/header
        elif path == "/device/info":
            device_id = self.headers.get("device-id", "unknown_device")
            response_data = {
                "code": 0,
                "msg": "success",
                "data": {
                    "Query method": "Header",
                    "Device ID": device_id,
                    "Battery": "85%",
                    "Firmware": "v2.0.1"
                }
            }

        # Case 5: Not found
        else:
            status_code = 404
            response_data = {"error": "endpoint not found"}

        # Send response
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

# Start server
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), MockRequestHandler) as httpd:
    print("==================================================")
    print(f"Mock API Server started: http://localhost:{PORT}")
    print("Available endpoints:")
    print(f"1. [Dict] http://localhost:{PORT}/health")
    print(f"2. [List] http://localhost:{PORT}/news/list")
    print(f"3. [Text] http://localhost:{PORT}/weather/simple")
    print(f"4. [Query/Header] http://localhost:{PORT}/device/info")
    print("==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
```
