# 교회 웹사이트 배포 가이드

## 📋 목차
1. [GCP Cloud Shell로 배포 (가장 간단)](#1-gcp-cloud-shell로-배포)
2. [GCP Compute Engine VM 배포](#2-gcp-compute-engine-vm-배포)
3. [Docker로 배포](#3-docker로-배포)
4. [수동 배포](#4-수동-배포)

---

## 1. GCP Cloud Shell로 배포 (가장 간단)

### 특징
- ✅ 가장 빠르고 간단
- ✅ 별도 VM 생성 불필요
- ⚠️ 비활성화 시 세션 종료 (일시적)
- ⚠️ 개발/테스트 용도로 적합

### 배포 방법

1. **GCP Console 접속**
   - https://console.cloud.google.com 접속
   - 우측 상단의 "Cloud Shell 활성화" 클릭

2. **배포 스크립트 실행**
   ```bash
   curl -sSL https://raw.githubusercontent.com/dhjin/church-website/main/gcp_cloud_shell_deploy.sh | bash
   ```

   또는 직접 클론:
   ```bash
   git clone https://github.com/dhjin/church-website.git
   cd church-website
   bash gcp_cloud_shell_deploy.sh
   ```

3. **웹사이트 접속**
   - Cloud Shell 상단의 "웹 미리보기" 버튼 클릭
   - "포트 8000에서 미리보기" 선택

4. **관리자 계정 생성**
   - `/login` 페이지에서 최초 관리자 계정 생성

### 유용한 명령어
```bash
# 로그 확인
tail -f ~/church-website/server.log

# 서버 중지
pkill -f 'python.*main.py'

# 서버 재시작
cd ~/church-website && ./restart.sh
```

---

## 2. GCP Compute Engine VM 배포

### 특징
- ✅ 영구적인 서비스
- ✅ 커스텀 도메인 연결 가능
- ✅ 프로덕션 환경에 적합
- 💰 VM 비용 발생

### 2-1. VM 생성

1. **GCP Console에서 VM 인스턴스 생성**
   - Compute Engine > VM 인스턴스 > 인스턴스 만들기
   - 권장 설정:
     - 머신 유형: e2-micro (무료 티어) 또는 e2-small
     - 부팅 디스크: Ubuntu 22.04 LTS
     - 방화벽: HTTP, HTTPS 트래픽 허용 체크

2. **VM 방화벽 규칙 추가**
   - VPC 네트워크 > 방화벽 규칙 > 방화벽 규칙 만들기
   - 이름: allow-church-website
   - 대상: 네트워크의 모든 인스턴스
   - 소스 IP 범위: 0.0.0.0/0
   - 프로토콜 및 포트: tcp:8000, tcp:80, tcp:443

### 2-2. VM 초기 설정

VM에 SSH 접속 후:
```bash
# GitHub에서 설정 스크립트 다운로드 및 실행
curl -sSL https://raw.githubusercontent.com/dhjin/church-website/main/setup_gcp.sh | bash
```

### 2-3. 배포

**방법 A: 로컬에서 배포 (권장)**
```bash
# 로컬 컴퓨터에서 실행
./deploy.sh [VM_외부_IP] [VM_사용자명]

# 예시
./deploy.sh 34.123.45.67 username
```

**방법 B: VM에서 직접 배포**
```bash
# VM에 SSH 접속 후
cd ~
git clone https://github.com/dhjin/church-website.git
cd church-website
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 2-4. Systemd 서비스 설정 (자동 시작)

```bash
# VM에서 실행
cd ~/church-website
sudo bash systemd_setup.sh
```

**서비스 관리 명령어:**
```bash
# 서비스 시작
sudo systemctl start church-website

# 서비스 중지
sudo systemctl stop church-website

# 서비스 재시작
sudo systemctl restart church-website

# 서비스 상태 확인
sudo systemctl status church-website

# 로그 확인
sudo journalctl -u church-website -f
```

### 2-5. 도메인 연결 (선택사항)

1. **고정 IP 예약**
   - VPC 네트워크 > 외부 IP 주소 > 고정 주소 예약

2. **DNS 설정**
   - 도메인 제공업체에서 A 레코드 추가
   - 호스트: @ (또는 www)
   - 값: VM 외부 IP 주소

3. **Nginx 설정 수정**
   ```bash
   sudo nano /etc/nginx/sites-available/church
   # server_name _; 를 실제 도메인으로 변경
   # server_name example.com www.example.com;
   sudo systemctl restart nginx
   ```

---

## 3. Docker로 배포

### 특징
- ✅ 환경 일관성
- ✅ 쉬운 스케일링
- ✅ 격리된 환경

### 사전 요구사항
```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo apt-get install docker-compose-plugin
```

### 배포 방법

```bash
# 코드 클론
git clone https://github.com/dhjin/church-website.git
cd church-website

# Docker Compose로 실행
docker compose up -d

# 로그 확인
docker compose logs -f

# 중지
docker compose down
```

**접속:**
- HTTP: http://[VM_IP]
- 애플리케이션 직접: http://[VM_IP]:8000

---

## 4. 수동 배포

### 로컬에서 테스트

```bash
# 1. 코드 클론
git clone https://github.com/dhjin/church-website.git
cd church-website

# 2. 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 서버 실행
python main.py

# 5. 브라우저에서 접속
# http://localhost:8000
```

---

## 🔐 보안 설정

### 데이터베이스 백업
```bash
# 백업
sqlite3 church.db ".backup church_backup_$(date +%Y%m%d).db"

# 복원
sqlite3 church.db ".restore church_backup_20240216.db"
```

### 환경 변수 설정 (.env 파일)
```bash
# .env 파일 생성
cat > .env << EOF
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./church.db
ALLOWED_HOSTS=your-domain.com
EOF
```

### SSL/HTTPS 설정 (Let's Encrypt)
```bash
# Certbot 설치
sudo apt-get install certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 자동 갱신 테스트
sudo certbot renew --dry-run
```

---

## 📊 모니터링

### 서버 상태 확인
```bash
# 프로세스 확인
ps aux | grep python

# 포트 확인
sudo netstat -tulpn | grep 8000

# 디스크 사용량
df -h

# 메모리 사용량
free -h
```

### 로그 모니터링
```bash
# 실시간 로그
tail -f server.log

# 에러 로그만 보기
grep ERROR server.log

# 최근 100줄
tail -100 server.log
```

---

## 🆘 문제 해결

### 포트가 이미 사용 중인 경우
```bash
# 8000 포트를 사용하는 프로세스 찾기
sudo lsof -i :8000

# 프로세스 종료
sudo kill -9 [PID]
```

### 데이터베이스 잠금 오류
```bash
# SQLite 데이터베이스 잠금 해제
fuser -k church.db
```

### 정적 파일이 로드되지 않는 경우
```bash
# 권한 확인
ls -la static/
chmod -R 755 static/

# Nginx 설정 테스트
sudo nginx -t
```

---

## 📞 지원

문제가 발생하면 GitHub Issues에 문의하세요:
https://github.com/dhjin/church-website/issues

---

## 📝 체크리스트

배포 전 확인사항:
- [ ] Python 3.8 이상 설치 확인
- [ ] requirements.txt 패키지 설치 완료
- [ ] 방화벽 포트 8000 (또는 80) 오픈
- [ ] 데이터베이스 파일 존재 확인 (또는 자동 생성)
- [ ] 관리자 계정 생성
- [ ] 정적 파일 경로 확인
- [ ] SSL 인증서 설정 (프로덕션)

배포 후 확인사항:
- [ ] 웹사이트 접속 확인
- [ ] 로그인 기능 테스트
- [ ] 설교 영상 재생 확인
- [ ] 교회소식 업로드 테스트
- [ ] 모바일 반응형 확인
- [ ] 자동 재시작 설정 확인
