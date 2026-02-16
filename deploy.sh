#!/bin/bash

# GCP VM 배포 스크립트
# 사용법: ./deploy.sh [VM_IP] [USERNAME]

set -e

VM_IP=${1:-"YOUR_VM_IP"}
USERNAME=${2:-"YOUR_USERNAME"}

echo "🚀 교회 웹사이트를 GCP VM에 배포합니다..."
echo "VM IP: $VM_IP"
echo "Username: $USERNAME"

# 1. 원격 서버에 디렉토리 생성
echo ""
echo "📁 Step 1: 원격 서버에 디렉토리 생성..."
ssh ${USERNAME}@${VM_IP} "mkdir -p ~/church-website"

# 2. 파일 전송 (데이터베이스 제외)
echo ""
echo "📦 Step 2: 파일 전송 중..."
rsync -avz --progress \
  --exclude 'venv/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '.git/' \
  --exclude 'church.db' \
  --exclude '*.log' \
  ./ ${USERNAME}@${VM_IP}:~/church-website/

# 3. 데이터베이스 파일 전송 (있는 경우)
echo ""
echo "💾 Step 3: 데이터베이스 파일 전송..."
if [ -f "church.db" ]; then
    scp church.db ${USERNAME}@${VM_IP}:~/church-website/
    echo "✅ 데이터베이스 파일 전송 완료"
else
    echo "⚠️  로컬 데이터베이스 없음 - 서버에서 새로 생성됩니다"
fi

# 4. 원격 서버에서 설정 및 실행
echo ""
echo "⚙️  Step 4: 원격 서버에서 애플리케이션 설정 중..."
ssh ${USERNAME}@${VM_IP} << 'ENDSSH'
cd ~/church-website

# Python 및 pip 설치 확인
if ! command -v python3 &> /dev/null; then
    echo "Python3 설치 중..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# 가상환경 생성
echo "가상환경 생성 중..."
python3 -m venv venv

# 패키지 설치
echo "Python 패키지 설치 중..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 기존 프로세스 종료
echo "기존 프로세스 종료 중..."
pkill -f "python.*main.py" || true

# 애플리케이션 실행
echo "애플리케이션 실행 중..."
nohup python main.py > server.log 2>&1 &

# 실행 확인
sleep 3
if pgrep -f "python.*main.py" > /dev/null; then
    echo "✅ 서버가 성공적으로 시작되었습니다!"
    echo "🌐 http://$(curl -s ifconfig.me):8000 에서 접속 가능합니다"
else
    echo "❌ 서버 시작 실패. 로그를 확인하세요:"
    tail -20 server.log
    exit 1
fi
ENDSSH

echo ""
echo "✅ 배포 완료!"
echo "🌐 웹사이트 접속: http://${VM_IP}:8000"
echo ""
echo "유용한 명령어:"
echo "  로그 확인: ssh ${USERNAME}@${VM_IP} 'tail -f ~/church-website/server.log'"
echo "  서버 재시작: ssh ${USERNAME}@${VM_IP} 'cd ~/church-website && ./restart.sh'"
echo "  서버 중지: ssh ${USERNAME}@${VM_IP} 'pkill -f python.*main.py'"
