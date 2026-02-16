#!/bin/bash

# GCP VM 초기 설정 스크립트
# VM에 SSH 접속 후 실행: bash setup_gcp.sh

set -e

echo "🔧 GCP VM 초기 설정을 시작합니다..."

# 시스템 업데이트
echo ""
echo "📦 Step 1: 시스템 패키지 업데이트..."
sudo apt-get update
sudo apt-get upgrade -y

# 필수 패키지 설치
echo ""
echo "📦 Step 2: 필수 패키지 설치..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    nginx \
    supervisor \
    sqlite3

# 방화벽 설정 (포트 8000 열기)
echo ""
echo "🔥 Step 3: 방화벽 설정..."
sudo ufw allow 8000/tcp || echo "UFW not available, skipping..."
sudo ufw allow 80/tcp || echo "UFW not available, skipping..."
sudo ufw allow 443/tcp || echo "UFW not available, skipping..."

# Nginx 설정 (리버스 프록시)
echo ""
echo "🌐 Step 4: Nginx 리버스 프록시 설정..."
sudo tee /etc/nginx/sites-available/church > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/$USER/church-website/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /uploads {
        alias /home/$USER/church-website/uploads;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Nginx 설정 활성화
sudo ln -sf /etc/nginx/sites-available/church /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

echo ""
echo "⚙️  Step 5: Supervisor 설정 (자동 시작)..."
sudo tee /etc/supervisor/conf.d/church.conf > /dev/null << EOF
[program:church-website]
directory=/home/$USER/church-website
command=/home/$USER/church-website/venv/bin/python main.py
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/$USER/church-website/supervisor.log
environment=PATH="/home/$USER/church-website/venv/bin"
EOF

sudo supervisorctl reread
sudo supervisorctl update

echo ""
echo "✅ GCP VM 초기 설정 완료!"
echo ""
echo "다음 단계:"
echo "1. 로컬에서 배포 스크립트 실행: ./deploy.sh $(curl -s ifconfig.me) $USER"
echo "2. 또는 GitHub에서 클론:"
echo "   cd ~"
echo "   git clone https://github.com/dhjin/church-website.git"
echo "   cd church-website"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "   python main.py"
echo ""
echo "🌐 웹사이트는 포트 80 (HTTP)으로 접속 가능합니다"
echo "   http://$(curl -s ifconfig.me)"
