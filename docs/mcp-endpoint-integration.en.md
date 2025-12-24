# MCP Endpoint Integration Guide

This guide uses the XiaoGe (虾哥) MCP calculator example to show how to connect a custom MCP service to your MCP Endpoint.

Prerequisite: your `xiaozhi-server` must already have MCP endpoint support enabled. If not, follow the enable guide: `docs/mcp-endpoint-enable.md`.

## How to add a simple MCP tool (calculator) to an agent

### Full-module deployment

If you run a full-module deployment, open the Management Console, go to **Agent Management**, click **Configure Roles** on an agent, and click the **Edit Functions** button next to **Intent Recognition**.

In the dialog you will see the **MCP Endpoint** area (usually showing that agent’s MCP Endpoint address). We'll use that address to extend the agent with an MCP-based calculator tool.

> Note: the MCP Endpoint address shown here is important — you will need it in the steps below.

### Single-module deployment

If you run a single-module deployment and have configured an MCP Endpoint address in your config, the server logs should show an entry like this when it starts:

```
250705[__main__]-INFO-Initialized component: vad success SileroVAD
250705[__main__]-INFO-Initialized component: asr success FunASRServer
250705[__main__]-INFO-OTA interface: http://192.168.1.25:8002/xiaozhi/ota/
250705[__main__]-INFO-Vision interface: http://192.168.1.25:8002/mcp/vision/explain
250705[__main__]-INFO-mcp endpoint: ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
250705[__main__]-INFO-Websocket address: ws://192.168.1.25:8000/xiaozhi/v1/
250705[__main__]-INFO-======= Above addresses are WebSocket protocol addresses — do not open them in a browser =======
250705[__main__]-INFO-To test WebSocket, open test/test_page.html in Chrome
250705[__main__]-INFO-=============================================================
```

The `mcp endpoint` value (for example `ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc`) is your MCP Endpoint address and is required for the steps below.

## Step 1 — Download the MCP calculator example

Open the calculator project in your browser: https://github.com/78/mcp-calculator

Click **Code → Download ZIP**, extract the downloaded archive (it may be named `mcp-calculator-main`) and rename the folder to `mcp-calculator`.

Enter the project directory and create a virtual/conda environment and install dependencies:

```bash
# enter project directory
cd mcp-calculator

conda remove -n mcp-calculator --all -y
conda create -n mcp-calculator python=3.10 -y
conda activate mcp-calculator

pip install -r requirements.txt
```

## Step 2 — Start the calculator MCP service

In the Management Console for the agent, copy the agent’s MCP Endpoint address (for example):

```
ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
```

Then export it in your shell and start the service:

```bash
export MCP_ENDPOINT=ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
python mcp_pipe.py calculator.py
```

### If you run the Management Console deployment

After starting the tool, return to the Management Console and refresh the MCP connection status; you should see the newly exposed tool listed for the agent.

### If you run the single-module deployment

When your device connects, the server logs should show messages similar to:

```
250705 -INFO-Initializing MCP endpoint: wss://2662r3426b.vicp.fun/mcp_e
250705 -INFO-Sending MCP endpoint initialization message
250705 -INFO-MCP endpoint connected
250705 -INFO-MCP endpoint initialization success
250705 -INFO-Tool handler initialized
250705 -INFO-MCP endpoint server info: name=Calculator, version=1.9.4
250705 -INFO-MCP endpoint tools supported: 1
250705 -INFO-All MCP endpoint tools retrieved, client ready
250705 -INFO-Tool cache refreshed
250705 -INFO-Current supported function list: [ 'get_time', 'get_lunar', 'play_music', 'get_weather', 'handle_exit_intent', 'calculator']
```

If the list includes `'calculator'`, your device can now call the calculator tool based on intent recognition.

---

*This is an English translation of `docs/mcp-endpoint-integration.md`. The original file remains unchanged.*