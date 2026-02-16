#!/bin/bash

# GCP Cloud Shell에서 실행하는 배포 스크립트
# Cloud Shell에서 실행: bash gcp_cloud_shell_deploy.sh

set -e

echo "🚀 GCP Cloud Shell에서 교회 웹사이트 배포를 시작합니다..."

# 1. GitHub에서 코드 클론
echo ""
echo "📦 Step 1: GitHub에서 코드 클론..."
if [ -d "church-website" ]; then
    echo "기존 디렉토리 삭제 중..."
    rm -rf church-website
fi

git clone https://github.com/dhjin/church-website.git
cd church-website

# 2. Python 가상환경 생성
echo ""
echo "🐍 Step 2: Python 가상환경 생성..."
python3 -m venv venv
source venv/bin/activate

# 3. 패키지 설치
echo ""
echo "📦 Step 3: Python 패키지 설치..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. 데이터베이스 초기화 (없는 경우)
echo ""
echo "💾 Step 4: 데이터베이스 확인..."
if [ ! -f "church.db" ]; then
    echo "⚠️  데이터베이스가 없습니다. 애플리케이션이 자동으로 생성합니다."
    echo "최초 실행 후 /login 에서 관리자 계정을 생성하세요."
fi

# 5. 기존 프로세스 종료
echo ""
echo "🔄 Step 5: 기존 프로세스 종료..."
pkill -f "python.*main.py" || echo "실행 중인 프로세스 없음"

# 6. 서버 실행
echo ""
echo "🚀 Step 6: 서버 시작..."
nohup python main.py > server.log 2>&1 &

# 7. 실행 확인
sleep 3
if pgrep -f "python.*main.py" > /dev/null; then
    echo ""
    echo "✅ 서버가 성공적으로 시작되었습니다!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🌐 웹 미리보기를 사용하여 접속하세요:"
    echo "   1. Cloud Shell 상단의 '웹 미리보기' 버튼 클릭"
    echo "   2. '포트 8000에서 미리보기' 선택"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 유용한 명령어:"
    echo "   로그 확인:     tail -f ~/church-website/server.log"
    echo "   서버 중지:     pkill -f 'python.*main.py'"
    echo "   서버 재시작:   cd ~/church-website && ./restart.sh"
    echo ""
    echo "⚠️  Cloud Shell은 비활성 상태가 되면 세션이 종료됩니다."
    echo "   영구적인 배포를 위해서는 Compute Engine VM을 사용하세요."
else
    echo "❌ 서버 시작 실패. 로그를 확인하세요:"
    tail -20 server.log
    exit 1
fi
