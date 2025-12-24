# RAGFlow Integration Guide

This guide has two main parts:

- Part I — How to deploy RAGFlow
- Part II — How to configure the RAGFlow service in the Management Console (智控台)

If you already know RAGFlow and have it deployed, skip Part I and go straight to Part II. If you prefer a guided deployment that reuses the project’s `mysql` and `redis` services (to save resources), start from Part I.

---

## Part I — Deploying RAGFlow

### Step 1 — Verify MySQL and Redis availability

RAGFlow requires a MySQL database. If you have already deployed the Management Console, you can reuse that MySQL instance.

On the host machine, check connectivity to MySQL and Redis ports using `telnet`:

```bash
telnet 127.0.0.1 3306
telnet 127.0.0.1 6379
```

If both ports are reachable, skip to Step 2.

If you cannot connect, identify how MySQL was installed:

- If MySQL was installed via a system package, the DB may be network-isolated; adjust that installation to expose port 3306.
- If MySQL/Redis were installed by this project using `docker-compose_all.yml`, edit the compose file to publish ports instead of using `expose`.

Change (example snippet):

Before:

```yaml
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    expose:
      - "3306:3306"
  xiaozhi-esp32-server-redis:
    ...
    expose:
      - 6379
```

After:

```yaml
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    ports:
      - "3306:3306"
  xiaozhi-esp32-server-redis:
    ...
    ports:
      - "6379:6379"
```

Then restart the stack in the folder that contains `docker-compose_all.yml` (for example `xiaozhi-server`):

```bash
cd xiaozhi-server
docker compose -f docker-compose_all.yml down
docker compose -f docker-compose_all.yml up -d
```

After restart, verify connectivity with `telnet` again.

### Step 2 — Create the RAGFlow database and user

If you can connect to MySQL, create a database and user for RAGFlow (example credentials used here):

```sql
CREATE DATABASE IF NOT EXISTS rag_flow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'rag_flow'@'%' IDENTIFIED BY 'infini_rag_flow';
GRANT ALL PRIVILEGES ON rag_flow.* TO 'rag_flow'@'%';
FLUSH PRIVILEGES;
```

### Step 3 — Download RAGFlow

Choose a directory on your host for RAGFlow (for example `/home/system/xiaozhi`) and clone the repository. This guide uses release `v0.22.0`:

```bash
git clone https://ghfast.top/https://github.com/infiniflow/ragflow.git
cd ragflow
git checkout v0.22.0
```

Enter the `docker` folder:

```bash
cd docker
```

Remove the MySQL dependency by deleting the `depends_on` block that references `mysql` from `ragflow-cpu` and `ragflow-gpu` services in `docker-compose.yml`.

Before:

```yaml
  ragflow-cpu:
    depends_on:
      mysql:
        condition: service_healthy
    profiles:
      - cpu
```

After:

```yaml
  ragflow-cpu:
    profiles:
      - cpu
```

Also remove the `mysql` and `redis` service definitions from `docker-compose-base.yml` so RAGFlow does not start its own DB services and instead uses your host-provided services.

### Step 4 — Update environment variables

Edit the `.env` file in `ragflow/docker` and set the DB/Redis connection details. Be sure to include `MYSQL_USER` — missing this key is a common reason RAGFlow fails to start. Repeat this checklist:

- If `MYSQL_USER` is missing, add it.
- If `MYSQL_USER` is missing, add it.
- If `MYSQL_USER` is missing, add it.

Example `.env` fragment:

```env
# Ports
SVR_WEB_HTTP_PORT=8008
SVR_WEB_HTTPS_PORT=8009

# MySQL (point to host DB)
MYSQL_HOST=host.docker.internal
MYSQL_PORT=3306
MYSQL_USER=rag_flow
MYSQL_PASSWORD=infini_rag_flow
MYSQL_DBNAME=rag_flow

# Redis
REDIS_HOST=host.docker.internal
REDIS_PORT=6379
REDIS_PASSWORD=
```

If your Redis has no password, update `service_conf.yaml.template` in the same folder to avoid the default password:

Before:

```yaml
redis:
  db: 1
  password: '${REDIS_PASSWORD:-infini_rag_flow}'
  host: '${REDIS_HOST:-redis}:6379'
```

After:

```yaml
redis:
  db: 1
  password: '${REDIS_PASSWORD:-}'
  host: '${REDIS_HOST:-redis}:6379'
```

### Step 5 — Start RAGFlow

From the `ragflow/docker` folder run:

```bash
docker-compose -f docker-compose.yml up -d
```

Check the logs, e.g.:

```bash
docker logs -n 20 -f docker-ragflow-cpu-1
```

If there are no errors, RAGFlow is running.

### Step 6 — Register an account

Open `http://127.0.0.1:8008` in your browser and sign up for an account. After registering, sign in.

If you want to disable public signup, set `REGISTER_ENABLED=0` in `ragflow/docker/.env` and restart the services:

```env
REGISTER_ENABLED=0
```

```bash
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.yml up -d
```

### Step 7 — Configure models inside RAGFlow

In the RAGFlow UI (`http://127.0.0.1:8008`), go to your avatar → Settings → **Model Providers**. Add the LLM provider and the Text Embedding provider you want to use, entering API keys where required. Then set them as the default models for LLM and Embedding in the settings UI.

---

## Part II — Configure RAGFlow in the Management Console (智控台)

### Step 1 — Create an API Key in RAGFlow

Log in to RAGFlow (`http://127.0.0.1:8008`). Go to your avatar → Settings → **API**, then **API Key** and click **Create new Key**. Copy the generated API Key for later use.

### Step 2 — Add RAGFlow service to Management Console

Ensure your Management Console version is **0.8.7** or newer and log in as a super-admin.

Enable the Knowledge Base feature: **Parameter Dictionary → System Feature Configuration**, check **Knowledge Base**, and save. The **Knowledge** menu should now appear.

Go to **Model Configuration → Knowledge**, find `RAG_RAGFlow` in the list and click **Edit**.

Set **Service URL** to your RAGFlow host (e.g., `http://192.168.1.100:8008`) and paste the previously copied **API Key** into the **API Key** field. Save the configuration.

### Step 3 — Create a knowledge base

In the Management Console, go to **Knowledge** and click **Add**. Enter a meaningful name and description for the knowledge base (for example `Company Overview` — description: “Company info such as contact, services, address, etc.”). Save.

Open the knowledge base you created and click **Add** (at the bottom-left) to upload documents. After uploading, click **Parse** on each document to generate slices/chunks, and then use **Recall Test** to validate retrieval.

### Step 4 — Enable the knowledge base for an agent

In the Management Console, go to **Agents**, open the agent you want to enable, click **Configure Roles**, then **Edit Functions**, and add the knowledge base to the agent functions. Save the agent configuration.

Now your agent can use RAGFlow as a knowledge source for retrieval-augmented generation.

---

*This is an English translation of `docs/ragflow-integration.md`. The original file is preserved.*