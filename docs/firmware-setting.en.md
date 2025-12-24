# Configure a custom server for the pre-built XiaoZhi firmware

## Step 1 — Confirm firmware version

This guide assumes you are using a pre-built XiaoZhi firmware of version 1.6.1 or newer:

https://github.com/78/xiaozhi-esp32/releases

## Step 2 — Prepare your OTA URL

If you followed the Full Module deployment guide, you should have an OTA URL for your server.

Open the OTA URL in your browser. Example:

```
https://2662r3426b.vicp.fun/xiaozhi/ota/
```

If the page shows “OTA interface is running normally, websocket cluster count: X”, proceed to the next step.

If it shows “OTA interface is not running normally”, you probably haven't configured the Websocket address in the Management Console. To fix it:

1. Log in to the Management Console with a super-admin account.
2. Click **Parameter Management** in the top menu.
3. Find the `server.websocket` entry and set your Websocket address. Example:

```
wss://2662r3426b.vicp.fun/xiaozhi/v1/
```

After saving, refresh the OTA page in your browser. If the page still indicates an issue, confirm that the websocket service is up and the address was saved correctly.

## Step 3 — Enter network configuration mode on the device

Put the device into network-configuration (pairing) mode. In the device UI, open **Advanced options** and enter your server's OTA address, then click **Save** and reboot the device.

![See — OTA address configuration](../docs/images/firmware-setting-ota.png)

## Step 4 — Wake XiaoZhi and check logs

Wake the device using the wake word and check the server logs/console output to confirm the device connects and normal activity appears.

## Common Issues

Reference these common problems and solutions:

- Why is speech being recognized as Korean/Japanese/English? — See: `./FAQ.md`
- "TTS task error: file not found" — See: `./FAQ.md`
- TTS frequently fails or times out — See: `./FAQ.md`
- WiFi can connect to my self-hosted server but cellular (4G) cannot — See: `./FAQ.md`
- How to improve XiaoZhi's response speed? — See: `./FAQ.md`
- XiaoZhi interrupts when I pause — See: `./FAQ.md`
- How to control lights, AC, or remotely power on/off with XiaoZhi — See: `./FAQ.md`

---

*This is an English translation of `docs/firmware-setting.md`. The original file remains unchanged.*