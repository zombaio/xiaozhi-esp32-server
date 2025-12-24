# How to get device info via MCP

This guide shows how to provide device information to MCP methods so your tools can access the device ID and other context variables.

Step 1 — Provide a custom agent base prompt

Copy the `agent-base-prompt.txt` from the `xiaozhi-server` directory into your `data` directory and rename it to `.agent-base-prompt.txt`.

Step 2 — Add device ID to the `<context>` section

Open `data/.agent-base-prompt.txt` and find the `<context>` section; add the following line inside it:

```
- **Device ID:** {{device_id}}
```

After the change, the `<context>` section should look similar to:

```
<context>
[IMPORTANT! The following information is provided in real time and does not require calling tools. Use them directly:]
- **Device ID:** {{device_id}}
- **Current time:** {{current_time}}
- **Today’s date:** {{today_date}} ({{today_weekday}})
- **Lunar date:** {{lunar_date}}
- **User city:** {{local_address}}
- **Local 7-day weather:** {{weather_info}}
</context>
```

Step 3 — Point your config to the custom prompt

Edit `data/.config.yaml` and change the `agent-base-prompt` template reference:

Before:

```
prompt_template: agent-base-prompt.txt
```

After:

```
prompt_template: data/.agent-base-prompt.txt
```

Step 4 — Restart the `xiaozhi-server` service

Step 5 — Add a `device_id` parameter to your MCP method

Add a parameter named `device_id` of type `string` and description `Device ID` to the MCP method definition.

Step 6 — Test

Wake XiaoZhi and invoke your MCP method. Verify that the method receives the `device_id` value as expected.

---

*This is an English translation of `docs/mcp-get-device-info.md`. The original file has been preserved.*