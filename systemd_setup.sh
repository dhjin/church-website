#!/bin/bash

# Systemd 서비스 설정 스크립트 (Supervisor 대신 사용 가능)
# VM에서 실행: sudo bash systemd_setup.sh

set -e

USER_NAME=${1:-$USER}
WORK_DIR="/home/$USER_NAME/church-website"

echo "🔧 Systemd 서비스를 설정합니다..."
echo "User: $USER_NAME"
echo "WorkDir: $WORK_DIR"

# Systemd 서비스 파일 생성
sudo tee /etc/systemd/system/church-website.service > /dev/null << EOF
[Unit]
Description=Church Website FastAPI Application
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$WORK_DIR
Environment="PATH=$WORK_DIR/venv/bin"
ExecStart=$WORK_DIR/venv/bin/python $WORK_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=append:$WORK_DIR/systemd.log
StandardError=append:$WORK_DIR/systemd.log

[Install]
WantedBy=multi-user.target
EOF

# Systemd 데몬 리로드
sudo systemctl daemon-reload

# 서비스 활성화 (부팅 시 자동 시작)
sudo systemctl enable church-website.service

# 서비스 시작
sudo systemctl start church-website.service

# 상태 확인
sleep 2
sudo systemctl status church-website.service

echo ""
echo "✅ Systemd 서비스 설정 완료!"
echo ""
echo "유용한 명령어:"
echo "  서비스 시작:   sudo systemctl start church-website"
echo "  서비스 중지:   sudo systemctl stop church-website"
echo "  서비스 재시작: sudo systemctl restart church-website"
echo "  서비스 상태:   sudo systemctl status church-website"
echo "  로그 확인:     sudo journalctl -u church-website -f"
echo "  또는:          tail -f $WORK_DIR/systemd.log"
