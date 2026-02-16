#!/bin/bash

# 서버 재시작 스크립트
# VM에서 실행: ./restart.sh

set -e

cd ~/church-website

echo "🔄 서버를 재시작합니다..."

# 기존 프로세스 종료
echo "기존 프로세스 종료 중..."
pkill -f "python.*main.py" || echo "실행 중인 프로세스 없음"

# 잠시 대기
sleep 2

# 가상환경 활성화 및 서버 실행
echo "서버 시작 중..."
source venv/bin/activate

# 백그라운드로 실행
nohup python main.py > server.log 2>&1 &

# 실행 확인
sleep 3
if pgrep -f "python.*main.py" > /dev/null; then
    echo "✅ 서버가 성공적으로 재시작되었습니다!"
    echo "프로세스 ID: $(pgrep -f "python.*main.py")"
    echo ""
    echo "로그 확인: tail -f ~/church-website/server.log"
else
    echo "❌ 서버 시작 실패. 로그를 확인하세요:"
    tail -20 server.log
    exit 1
fi
