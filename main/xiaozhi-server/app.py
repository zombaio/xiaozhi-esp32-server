import sys
import uuid
import signal
import asyncio
from aioconsole import ainput
from config.settings import load_config
from config.logger import setup_logging
from core.utils.util import get_local_ip, validate_mcp_endpoint
from core.http_server import SimpleHttpServer
from core.websocket_server import WebSocketServer
from core.utils.util import check_ffmpeg_installed
from core.utils.gc_manager import get_gc_manager

TAG = __name__
logger = setup_logging()


async def wait_for_exit() -> None:
    """
    Block until Ctrl‑C / SIGTERM is received.
    - Unix: use add_signal_handler
    - Windows: relies on KeyboardInterrupt
    """
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    if sys.platform != "win32":  # Unix / macOS
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)
        await stop_event.wait()
    else:
        # Windows: await a perpetually pending fut,
        # Make KeyboardInterrupt bubble up to asyncio.run, thus eliminating the problem of residual ordinary threads causing process exit blocking.
        try:
            await asyncio.Future()
        except KeyboardInterrupt:  # Ctrl‑C
            pass


async def monitor_stdin():
    """Monitor standard input and consume Enter presses"""
    while True:
        await ainput()  # Asynchronously wait for input and consume Enter presses


async def main():
    check_ffmpeg_installed()
    config = load_config()

    # auth_key priority: configuration file server.auth_key > manager-api.secret > automatically generated
    # auth_key is used for JWT authentication, such as JWT authentication for visual analytics interfaces, token generation for OTA interfaces, and WebSocket authentication
    # Retrieve auth_key from the configuration file
    auth_key = config["server"].get("auth_key", "")
    
    # Validate auth_key; if invalid, try using manager-api.secret
    if not auth_key or len(auth_key) == 0 or "你" in auth_key:
        auth_key = config.get("manager-api", {}).get("secret", "")
        # Validate secret; if invalid, generate a random key
        if not auth_key or len(auth_key) == 0 or "你" in auth_key:
            auth_key = str(uuid.uuid4().hex)
    
    config["server"]["auth_key"] = auth_key

    # Add stdin monitor task
    stdin_task = asyncio.create_task(monitor_stdin())

    # Start the global GC manager (clean every 5 minutes).
    gc_manager = get_gc_manager(interval_seconds=300)
    await gc_manager.start()

    # Start the WebSocket server
    ws_server = WebSocketServer(config)
    ws_task = asyncio.create_task(ws_server.start())
    # Start Simple HTTP Server
    ota_server = SimpleHttpServer(config)
    ota_task = asyncio.create_task(ota_server.start())

    read_config_from_api = config.get("read_config_from_api", False)
    port = int(config["server"].get("http_port", 8003))
    if not read_config_from_api:
        logger.bind(tag=TAG).info(
            "OTA interface is\t\thttp://{}:{}/xiaozhi/ota/",
            get_local_ip(),
            port,
        )
    logger.bind(tag=TAG).info(
        "Visual analysis interface is\thttp://{}:{}/mcp/vision/explain",
        get_local_ip(),
        port,
    )
    mcp_endpoint = config.get("mcp_endpoint", None)
    if mcp_endpoint is not None and "你" not in mcp_endpoint:
        # Validate MCP endpoint format
        if validate_mcp_endpoint(mcp_endpoint):
            logger.bind(tag=TAG).info("MCP access point is\t{}", mcp_endpoint)
            # Convert /mcp/ endpoint to /call/ for outgoing calls
            mcp_endpoint = mcp_endpoint.replace("/mcp/", "/call/")
            config["mcp_endpoint"] = mcp_endpoint
        else:
            logger.bind(tag=TAG).error("The MCP access point does not conform to the specifications")
            config["mcp_endpoint"] = "your MCP websocket endpoint address"

    # Get the WebSocket configuration and use the safe default values.
    websocket_port = 8000
    server_config = config.get("server", {})
    if isinstance(server_config, dict):
        websocket_port = int(server_config.get("port", 8000))

    logger.bind(tag=TAG).info(
        "The WebSocket address is\tws://{}:{}/xiaozhi/v1/",
        get_local_ip(),
        websocket_port,
    )

    logger.bind(tag=TAG).info(
        "=== The address above is a WebSocket protocol address; please do not access it using a browser ==="
    )
    logger.bind(tag=TAG).info(
        "To test WebSocket, please open the test_page.html file located in the test directory using Google Chrome."
    )
    logger.bind(tag=TAG).info(
        "=============================================================\n"
    )

    try:
        await wait_for_exit()  # Block until an exit signal is received
    except asyncio.CancelledError:
        print("Task cancelled, resources being cleaned up...")
    finally:
        # Stop the global GC manager
        await gc_manager.stop()

        # Cancel all tasks (important fix)
        stdin_task.cancel()
        ws_task.cancel()
        if ota_task:
            ota_task.cancel()

        # Wait for tasks to terminate (include a timeout)
        await asyncio.wait(
            [stdin_task, ws_task, ota_task] if ota_task else [stdin_task, ws_task],
            timeout=3.0,
            return_when=asyncio.ALL_COMPLETED,
        )
        print("The server has been shut down and the program has exited")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Manually interrupting the program will terminate it")
