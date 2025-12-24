# Weather Plugin — Usage Guide

## Overview

The `get_weather` plugin is one of the core features of the XiaoZhi ESP32 voice assistant. It enables voice-based weather queries for locations across China and returns current weather and 7-day forecasts. The plugin uses the QWeather (HeWeather) API.

## API Key — Quick Setup

### 1. Register a QWeather account

1. Open the QWeather Console: https://console.qweather.com/
2. Register an account and verify your email.
3. Log in to the console.

### 2. Create a project and obtain an API Key

1. In the console, go to **Project Management** → **Create Project**.
2. Provide a project name (for example: "XiaoZhi Voice Assistant") and save.
3. Inside the project, click **Create Credentials** and choose **API Key** authentication.
4. Save and copy the generated **API Key** — this is one of the two required values.

### 3. Get your API Host

1. In the console, go to **Settings** → **API Host**.
2. Copy the assigned **API Host** address — this is the second required value.

After these steps you will have two required values: **API Key** and **API Host**.

## Configuration (choose one)

### Option 1 — Configure in the Management Console (recommended)

1. Log in to the Management Console.
2. Open **Role Configuration**, select the agent you want to configure, and click **Edit Functions**.
3. Find and enable the **Weather Query** plugin.
4. Paste your **API Key** into the “Weather plugin API key” field.
5. Paste your **API Host** into the “Developer API Host” field.
6. Save the plugin settings and then save the agent configuration.

### Option 2 — Configure in single-module `xiaozhi-server` (data file)

Edit `data/.config.yaml` and add the weather plugin settings:

```yaml
plugins:
  get_weather:
    api_key: "YOUR_QWEATHER_API_KEY"
    api_host: "YOUR_QWEATHER_API_HOST"
    default_location: "Your default city, e.g. Guangzhou"
```

- `api_key`: your QWeather API key
- `api_host`: your QWeather API host (from the console)
- `default_location`: optional default city for quick queries

---

*This is an English translation of `docs/weather-integration.md`. The original file remains unchanged.*