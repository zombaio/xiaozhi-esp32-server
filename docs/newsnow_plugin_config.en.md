# get_news_from_newsnow Plugin — News Source Configuration Guide

## Overview

The `get_news_from_newsnow` plugin now supports dynamically configuring news sources through the Web management console — no code changes are required. You can configure different news sources for each agent in the Management Console.

## How to configure

### 1) Configure via the Web management console (recommended)

1. Log in to the Management Console.
2. Open the **Role Configuration** page.
3. Select the agent you want to configure.
4. Click **Edit Functions**.
5. In the right-side parameter area find the **newsnow news aggregator** plugin.
6. Enter the news sources as a semicolon-separated list of Chinese names in the **News Source Configuration** field.

### 2) Configure via the config file

Add (or update) the plugin configuration in `config.yaml`:

```yaml
plugins:
  get_news_from_newsnow:
    url: "https://newsnow.busiyi.world/api/s?id="
    news_sources: "澎湃新闻;百度热搜;财联社;微博;抖音"
```

## News source format

The news source list should be a semicolon-separated string of Chinese names, for example:

```
中文名称1;中文名称2;中文名称3
```

### Example

```
澎湃新闻;百度热搜;财联社;微博;抖音;知乎;36氪
```

## Supported news sources

The plugin recognizes these Chinese names (the configured names must match exactly as defined in the internal `CHANNEL_MAP`):

- 澎湃新闻
- 百度热搜
- 财联社
- 微博
- 抖音
- 知乎
- 36氪
- 华尔街见闻
- IT之家
- 今日头条
- 虎扑
- 哔哩哔哩
- 快手
- 雪球
- 格隆汇
- 法布财经
- 金十数据
- 牛客
- 少数派
- 稀土掘金
- 凤凰网
- 虫部落
- 联合早报
- 酷安
- 远景论坛
- 参考消息
- 卫星通讯社
- 百度贴吧
- 靠谱新闻
- and more...

> Note: These are the Chinese display names the plugin accepts. The plugin maps each Chinese name to an internal English ID (e.g., "澎湃新闻" → "thepaper") when calling the remote API.

## Default configuration

If no news sources are configured, the plugin uses the default:

```
澎湃新闻;百度热搜;财联社
```

## Usage

1. Configure the news sources either in the Web UI or in the config file (use Chinese names, separated by *English semicolons* `;`).
2. Ask the agent to "播报新闻" (read news) or "获取新闻" (get news).
3. To target a source, say e.g. "播报澎湃新闻" or "获取百度热搜".
4. To get more details about an item, say "详细介绍这条新闻".

## How it works

1. The plugin accepts a Chinese name as input (e.g., "澎湃新闻").
2. The plugin looks up that name in its configured news-source list and maps it to an internal English ID (e.g., `thepaper`).
3. The plugin calls the remote API using the English ID to retrieve news items.
4. The news content is returned to the user.

## Notes & Best Practices

- The configured Chinese names must match the names defined in the plugin's `CHANNEL_MAP` exactly.
- After changing configuration, restart the server or reload the configuration.
- If a configured news source is invalid or unavailable, the plugin will fall back to the default sources.
- Use English semicolons (`;`) to separate multiple sources; do not use Chinese semicolons (`；`).

---

*This is an English translation of `docs/newsnow_plugin_config.md`. The original file has been preserved.*