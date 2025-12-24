# Voiceprint (Speaker Recognition) Integration Guide

This guide contains three parts:
- 1) How to deploy the voiceprint recognition service
- 2) How to configure voiceprint for full-module deployments
- 3) How to configure voiceprint for minimal single-module deployments

---

## 1) Deploy the voiceprint recognition service

### Step 1 — Download the project source

Open the project page in your browser: https://github.com/xinnan-tech/voiceprint-api

Click **Code → Download ZIP**, extract the archive (it may be named `voiceprint-api-main`) and rename the folder to `voiceprint-api`.

### Step 2 — Verify MySQL availability

Voiceprint requires a MySQL database. If you already deployed the Management Console, you can reuse its database.

Check connectivity from your host to MySQL with `telnet`:

```
telnet 127.0.0.1 3306
```

If you can connect, skip to Step 3.

If you cannot connect, determine how MySQL was installed:
- If installed from a package, it may be network-isolated — make it reachable on port 3306.
- If MySQL was deployed via the project's `docker-compose_all.yml`, edit that compose file to publish port 3306 instead of `expose`.

Example change in `docker-compose_all.yml`:

Before:

```yaml
  xiaozhi-esp32-server-db:
    networks:
      - default
    expose:
      - "3306:3306"
```

After:

```yaml
  xiaozhi-esp32-server-db:
    networks:
      - default
    ports:
      - "3306:3306"
```

Then restart the stack and verify connectivity again.

### Step 3 — Create the database and table

Create a database named `voiceprint_db` and a `voiceprints` table:

```sql
CREATE DATABASE voiceprint_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE voiceprint_db;

CREATE TABLE voiceprints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    speaker_id VARCHAR(255) NOT NULL UNIQUE,
    feature_vector LONGBLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_speaker_id (speaker_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Step 4 — Configure DB connection

Inside the `voiceprint-api` folder, create a `data` directory and copy `voiceprint.yaml` from the repo root into it, renaming it to `.voiceprint.yaml`.

Edit `.voiceprint.yaml` and set your MySQL connection information:

```yaml
mysql:
  host: "127.0.0.1"
  port: 3306
  user: "root"
  password: "your_password"
  database: "voiceprint_db"
```

Important: if you run the voiceprint service in Docker, set `host` to the LAN IP of the machine that runs MySQL (not `localhost`).

### Step 5 — Start the service

Docker is recommended. From the project root:

```bash
cd voiceprint-api
# cleanup
docker compose -f docker-compose.yml down
docker stop voiceprint-api || true
docker rm voiceprint-api || true
docker rmi ghcr.nju.edu.cn/xinnan-tech/voiceprint-api:latest || true
# start
docker compose -f docker-compose.yml up -d
# view logs
docker logs -f voiceprint-api
```

The service logs will show a health URL, for example:

```
250711 INFO-Voiceprint health URL: http://127.0.0.1:8005/voiceprint/health?key=abcd
```

Because the service runs in Docker, replace the container-local address with your host LAN IP before using it. For example:

```
http://127.0.0.1:8005/voiceprint/health?key=abcd
→
http://192.168.1.25:8005/voiceprint/health?key=abcd
```

Open the health URL in your browser — a successful response looks like:

```json
{"total_voiceprints":0,"status":"healthy"}
```

Keep the modified health URL — you will need it in the next steps.

---

## 2) Full-module deployment: configure voiceprint

### Step 1 — Configure the service URL

Enable the voiceprint feature in the Management Console: **Parameter Dictionary → System Feature Configuration**, check **Voiceprint**, and save. The **Voiceprint** button will appear on agent cards.

In **Parameter Management**, search for `server.voice_print` and set it to the voiceprint health/service URL you obtained earlier, then save.

If saving fails, check network/firewall rules and ensure you used the correct LAN IP.

### Step 2 — Set agent memory mode

In the agent’s role configuration, set memory to **Local short-term memory** and enable **Report text + audio**.

### Step 3 — Talk to the agent

Power on your device and speak naturally to it so the system can collect voice samples.

### Step 4 — Register a voiceprint

In the Management Console, open **Agent Management**, click a specific agent, then click **Voiceprint**. Use the **Add** button to register a voice sample for a person. In the dialog, include a meaningful description (e.g., profession, hobbies) to help the agent understand the speaker.

### Step 5 — Test

Ask the device "Do you know who I am?" If it can identify the speaker, voiceprint recognition is working.

---

## 3) Minimal single-module deployment

### Step 1 — Configure the service URL and speakers

Open `xiaozhi-server/data/.config.yaml` (create it if missing) and add:

```yaml
voiceprint:
  url: <your-voiceprint-service-url>
  speakers:
    - "test1,张三,张三是一个程序员"
    - "test2,李四,李四是一个产品经理"
    - "test3,王五,王五是一个设计师"
```

Paste the health/service URL (from earlier) into `url`. The `speakers` list defines `speaker_id,name,description` entries; `speaker_id` must match the ID used when registering voice samples.

### Step 2 — Register voiceprints

If the voiceprint service is running locally, open `http://localhost:8005/voiceprint/docs` to view the API docs.

Register a voiceprint via POST to `/voiceprint/register`. Use Bearer token authentication — the token is the `key` value from the health URL (e.g., `abcd` in `?key=abcd`). Example:

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "speaker_id=your_speaker_id_here" \
  -F "file=@/path/to/your/file.wav" \
  http://localhost:8005/voiceprint/register
```

The `speaker_id` must match one of the entries you configured in `.config.yaml`.

### Step 3 — Start services

Start both the XiaoZhi server and the voiceprint service. After devices are running and samples are registered, voiceprint-based identification should work.

---

*This is an English translation of `docs/voiceprint-integration.md`. The original file has been preserved.*