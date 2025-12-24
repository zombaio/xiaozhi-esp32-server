# Auto-upgrade method for full-stack source deployment

This guide shows how to automate pulling source updates, building, and restarting services for a full-stack (all modules) source deployment — a simple DevOps flow to enable efficient upgrades.

Our test platform https://2662r3426b.vicp.fun has used this method since launch with good results.

Refer to the video walkthrough by Bilibili creator 毕乐labs: "Guide to auto-updating the open-source Xiaozhi server and configuring the latest MCP endpoint" (https://www.bilibili.com/video/BV15H37zHE7Q).

# Requirements
- The machine (server or workstation) runs Linux
- You have already successfully run the full manual deployment at least once
- You want to follow upstream changes and prefer an automated update workflow

Note: the second requirement is mandatory. The tutorial assumes you already have JDK, Node.js, Conda, and other components installed and working — if you haven’t completed the manual run-through, some referenced files and steps may be unclear.

# What this tutorial achieves
- Works around network restrictions when fetching source updates in China
- Automatically fetches and builds the frontend
- Automatically fetches and builds the Java service, kills any process using port 8002, and restarts the service
- Automatically fetches Python code, kills any process using port 8000, and restarts the server

# Step 1 — Choose a project directory

For example, I use a clean directory:

```
/home/system/xiaozhi
```

# Step 2 — Clone the repository

Run (suitable for servers in China without VPN):

```bash
cd /home/system/xiaozhi
git clone https://ghproxy.net/https://github.com/xinnan-tech/xiaozhi-esp32-server.git
```

After this you will have a `xiaozhi-esp32-server` folder containing the project source.

# Step 3 — Copy base files

If you already have a working setup, you should have the FunASR model file and your personal config file:

- `xiaozhi-server/models/SenseVoiceSmall/model.pt`
- `xiaozhi-server/data/.config.yaml`

Copy these files into the new repository tree, for example:

```bash
# Create directories
mkdir -p /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/data/

cp /path/to/your/.config.yaml /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/data/.config.yaml
cp /path/to/your/model.pt /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/models/SenseVoiceSmall/model.pt
```

# Step 4 — Create three auto-update scripts

## 4.1 Auto-build the `manager-web` frontend

Create `/home/system/xiaozhi/update_8001.sh` with:

```bash
cd /home/system/xiaozhi/xiaozhi-esp32-server
git fetch --all
git reset --hard
git pull origin main

cd /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-web
npm install
npm run build
rm -rf /home/system/xiaozhi/manager-web
mv /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-web/dist /home/system/xiaozhi/manager-web
```

Make it executable:

```bash
chmod 777 update_8001.sh
```

## 4.2 Auto-build and restart `manager-api` (Java)

Create `/home/system/xiaozhi/update_8002.sh` with:

```bash
cd /home/system/xiaozhi/xiaozhi-esp32-server
git pull origin main

cd /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-api
rm -rf target
mvn clean package -Dmaven.test.skip=true
cd /home/system/xiaozhi/

# Find PID that uses port 8002
PID=$(sudo netstat -tulnp | grep 8002 | awk '{print $7}' | cut -d'/' -f1)

rm -rf /home/system/xiaozhi/xiaozhi-esp32-api.jar
mv /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-api/target/xiaozhi-esp32-api.jar /home/system/xiaozhi/xiaozhi-esp32-api.jar

# If a PID was found, kill it
if [ -z "$PID" ]; then
  echo "No process found using port 8002"
else
  echo "Found process using port 8002, PID: $PID"
  kill -9 $PID
  kill -9 $PID
  echo "Killed process $PID"
fi

nohup java -jar xiaozhi-esp32-api.jar --spring.profiles.active=dev &

tail -f nohup.out
```

Make it executable:

```bash
chmod 777 update_8002.sh
```

## 4.3 Auto-update and restart the Python server

Create `/home/system/xiaozhi/update_8000.sh` with:

```bash
cd /home/system/xiaozhi/xiaozhi-esp32-server
git pull origin main

# Find PID that uses port 8000
PID=$(sudo netstat -tulnp | grep 8000 | awk '{print $7}' | cut -d'/' -f1)

# If a PID was found, kill it
if [ -z "$PID" ]; then
  echo "No process found using port 8000"
else
  echo "Found process using port 8000, PID: $PID"
  kill -9 $PID
  kill -9 $PID
  echo "Killed process $PID"
fi

cd main/xiaozhi-server
# Initialize conda environment
source ~/.bashrc
conda activate xiaozhi-esp32-server
pip install -r requirements.txt
nohup python app.py >/dev/null &
tail -f /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/tmp/server.log
```

Make it executable:

```bash
chmod 777 update_8000.sh
```

# Routine updates

With the scripts in place, routine updates are as simple as running them in order:

```bash
cd /home/system/xiaozhi
# Update and start Java program (manager-api)
./update_8001.sh
# Update the web frontend
./update_8002.sh
# Update and start Python server
./update_8000.sh

# To view Java logs later
tail -f nohup.out
# To view Python logs later
tail -f /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/tmp/server.log
```

# Notes / Caveats

Our test platform (https://2662r3426b.vicp.fun) uses nginx as a reverse proxy. See nginx configuration discussion here: https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791

## FAQ

### 1) Why don't I see port 8001?
A: Port 8001 is used only during development for serving the frontend (`npm run serve`). For server deployments, build the frontend into static HTML (as in this guide) and serve it via nginx rather than launching `npm run serve`.

### 2) Do I need to manually run database SQL updates each time?
A: No. The project uses **Liquibase** to manage database schema updates and will automatically run new migration scripts as needed.
