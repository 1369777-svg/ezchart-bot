# Deployment Guide

## Option 1: Render (recommended for MVP)

Pros: 5-minute setup, GitHub integration.
Cons: Sleeps after 15 min of inactivity.

Steps:

1. Push the repo to GitHub
2. Open render.com, then New -> Web Service
3. Connect the ezchart-bot repo
4. Settings:
   - Environment: Python 3.11
   - Build Command: pip install -r requirements.txt
   - Start Command: python -m src.main
   - Instance Type: Free
5. Environment Variables:
   - TELEGRAM_TOKEN
   - GEMINI_API_KEY
   - GEMINI_MODEL=gemini-3.6-flash
   - LOG_LEVEL=INFO
   - RATE_LIMIT_SEC=10
6. Deploy

## Option 2: Oracle Cloud Always Free (24/7)

Pros: 1 CPU and 1 GB RAM free forever.
Cons: 15-minute setup.

Steps:

1. Create account at cloud.oracle.com
2. Compute -> Instances -> Create
   - Image: Ubuntu 22.04
   - Shape: VM.Standard.A1.Flex (ARM, 1 OCPU, 1 GB) — Always Free
3. SSH: ssh ubuntu@public-ip
4. Install dependencies:
   sudo apt update && sudo apt install -y python3.11 python3.11-venv git
   git clone https://github.com/1369777-svg/ezchart-bot.git
   cd ezchart-bot
   python3.11 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
5. Create .env: nano .env
6. systemd service at /etc/systemd/system/ezchart.service:

   [Unit]
   Description=EZChart Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/ezchart-bot
   EnvironmentFile=/home/ubuntu/ezchart-bot/.env
   ExecStart=/home/ubuntu/ezchart-bot/venv/bin/python -m src.main
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target

7. Enable:
   sudo systemctl daemon-reload
   sudo systemctl enable --now ezchart
   sudo systemctl status ezchart

## Option 3: Docker

docker build -t ezchart .
docker run -d --env-file .env --name ezchart ezchart

## Free Tier Comparison

| Platform | CPU | RAM | Sleep | Notes |
|----------|-----|-----|-------|-------|
| Render | 0.1 | 512 MB | 15 min | Good for start |
| Oracle Always Free | 1 ARM | 1 GB | None | Best value |
| Koyeb | 0.1 | 256 MB | None | Good backup |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| TELEGRAM_TOKEN | yes | - | Bot token from BotFather |
| GEMINI_API_KEY | yes | - | API key from Google AI Studio |
| GEMINI_MODEL | no | gemini-3.6-flash | Model name |
| LOG_LEVEL | no | INFO | Logging level |
| RATE_LIMIT_SEC | no | 10 | Anti-spam window |