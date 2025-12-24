# How to build Docker images locally

The project supports automatic Docker builds on GitHub, but this guide is for people who want to build the Docker images locally.

1. Install Docker (example for Debian/Ubuntu):

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

2. Build the Docker images

```bash
# From the project root

# Build the server image
docker build -t xiaozhi-esp32-server:server_latest -f ./Dockerfile-server .

# Build the web image
docker build -t xiaozhi-esp32-server:web_latest -f ./Dockerfile-web .

# After the images are built, start the stack with docker compose
# Make sure your docker-compose.yml references the images you built locally
cd main/xiaozhi-server
docker compose up -d
```

That's it — you now have locally built images and can run the stack using Docker Compose. If you need an arm64 image, follow the instructions in `docs/docker-build.md` for building multi-arch images or consult `docker-build.md` for further details.