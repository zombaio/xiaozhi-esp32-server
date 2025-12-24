# ESP32 Firmware Build Guide

## Step 1 — Prepare your OTA URL

If you are using this project (v0.3.12), both the Simple Server deployment and the Full Module deployment provide an OTA (over-the-air) URL.

Because the OTA URL is configured differently for the two deployment types, choose the instructions below that match your deployment.

### Simple Server deployment

Open the OTA URL in your browser. Example:

```
http://192.168.1.25:8003/xiaozhi/ota/
```

If the page shows “OTA interface is running normally, the websocket address to send to devices is: ws://xxx:8000/xiaozhi/v1/”, then you can test the websocket address using the project's `test_page.html` to confirm it connects.

If you cannot access the page, edit your `.config.yaml` and update the `server.websocket` address, then restart the server and test again. Repeat until `test_page.html` can access the websocket address successfully.

Once that works, continue to Step 2.

### Full Module deployment

Open the OTA URL in your browser. Example:

```
http://192.168.1.25:8002/xiaozhi/ota/
```

If the page shows “OTA interface is running normally, websocket cluster count: X”, proceed to Step 2.

If it shows “OTA interface is not running normally”, you probably haven’t configured the Websocket address in the Management Console. To fix it:

1. Log in to the Management Console with a super-admin account.
2. Go to **Parameter Management**.
3. Find the `server.websocket` entry and set your Websocket address (for example):

```
ws://192.168.1.25:8000/xiaozhi/v1/
```

Save the configuration, then refresh the OTA interface page in your browser. If it is still not working, verify that the Websocket service is running and that the address is configured correctly.

## Step 2 — Set up the build environment

Follow this guide to set up the ESP-IDF 5.3.2 development environment on Windows:

[Windows: Set up ESP-IDF 5.3.2 and build XiaoZhi](https://icnynnzcwou8.feishu.cn/wiki/JEYDwTTALi5s2zkGlFGcDiRknXf)

Complete the environment setup before proceeding.

## Step 3 — Open the project configuration

Clone or download the `xiaozhi-esp32` repository:

https://github.com/78/xiaozhi-esp32

Open the file:

```
xiaozhi-esp32/main/Kconfig.projbuild
```

## Step 4 — Modify the OTA URL

Find the `OTA_URL` default value and replace the example URL with your own OTA URL.

Before:

```
config OTA_URL
    string "Default OTA URL"
    default "https://api.tenclass.net/xiaozhi/ota/"
    help
        The application will access this URL to check for new firmwares and server address.
```

After (example):

```
config OTA_URL
    string "Default OTA URL"
    default "http://192.168.1.25:8002/xiaozhi/ota/"
    help
        The application will access this URL to check for new firmwares and server address.
```

Replace the URL above with your own OTA endpoint.

## Step 5 — Set build parameters

Open a terminal in the `xiaozhi-esp32` root directory and run:

```bash
cd xiaozhi-esp32
# Example: if your board is ESP32-S3, set the build target accordingly
idf.py set-target esp32s3
# Enter menu configuration
idf.py menuconfig
```

Inside the menu config, go to **Xiaozhi Assistant** and set `BOARD_TYPE` to your board model. Save and exit, then return to the terminal.

## Step 6 — Build the firmware

Run the build:

```
idf.py build
```

## Step 7 — Package the firmware binaries

Run the packaging script:

```
cd scripts
python release.py
```

After the script finishes, you should find the firmware file `merged-binary.bin` in the project's `build` directory. This is the binary file to flash onto your hardware.

Note: if you see a `zip`-related error while packaging but `merged-binary.bin` is created in the `build` directory, you can ignore that error — it generally does not affect the generated firmware.

## Step 8 — Flash the firmware

Connect the ESP32 device to your computer and open the ESP Launchpad web flasher:

```
https://espressif.github.io/esp-launchpad/
```

Follow the instructions in the tutorial “Flash tool / Web flashing (no IDF dev environment)” — specifically the section “Method 2: ESP-Launchpad browser web flashing”, starting from step 3 "Flash firmware / download to board".

After flashing and the device connects to the network, wake XiaoZhi using the wake word and observe the server console for status and logs.

## Common Issues

Here are some common issues for reference:

- Why does my speech get recognized as Korean/Japanese/English? — See: `./FAQ.md`
- Why does it say "TTS task error: file not found"? — See: `./FAQ.md`
- TTS often fails or times out — See: `./FAQ.md`
- WiFi can connect to my self-hosted server but cellular (4G) cannot — See: `./FAQ.md`
- How to improve XiaoZhi's response speed? — See: `./FAQ.md`
- I speak slowly and XiaoZhi interrupts me — See: `./FAQ.md`
- I want to control lights, AC, or remotely power on/off via XiaoZhi — See: `./FAQ.md`


---

*This is an English translation of `docs/firmware-build.md`. Both files are kept in the repository.*