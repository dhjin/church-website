# 더하는 교회 홈페이지

FastAPI와 SQLite를 사용한 깔끔하고 현대적인 교회 웹사이트입니다.

## 교회 정보

- **교회명**: 더하는 교회
- **소속**: 기독교 한국침례회
- **교회대표**: 김한기 목사
- **주소**: 대전시 유성구 학하동 755-6 1층

## 주요 기능

### 사용자 기능
- 📖 최근 설교 목록
- 📰 교회소식 게시판 (조회수 카운트)
- ℹ️ 교회 소개 (소속, 담임목사 정보 포함)
- 📍 찾아오시는 길 (네이버 지도 연동)
- 📞 연락처 정보
- 📱 완벽한 모바일 반응형 디자인
  - 모바일 햄버거 메뉴
  - 터치 친화적 UI
  - 다양한 화면 크기 지원 (스마트폰, 태블릿, 데스크톱)

### 관리자 기능
- 🔐 로그인/로그아웃 시스템
- 👥 사용자 권한 관리 (관리자/일반 사용자)
- ✍️ 교회소식 작성/삭제
- 🖼️ 이미지 업로드 기능
- 📝 교회 소개 내용 수정
- 📊 관리자 대시보드

## 기술 스택

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Template Engine**: Jinja2

## 설치 방법

### 1. 가상환경 생성 및 활성화 (권장)

```bash
cd /Users/admin/church/church-website
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
```

### 2. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

## 실행 방법

### 개발 서버 실행

```bash
python main.py
```

또는

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 웹사이트 접속

브라우저에서 다음 주소로 접속하세요:

```
http://localhost:8000
```

## API 엔드포인트

- `GET /` - 메인 홈페이지
- `GET /api/sermons` - 설교 목록 조회 (JSON)
- `GET /api/events` - 행사 일정 조회 (JSON)
- `GET /api/announcements` - 공지사항 조회 (JSON)

### API 사용 예시

```bash
# 설교 목록 조회
curl http://localhost:8000/api/sermons

# 행사 일정 조회
curl http://localhost:8000/api/events

# 공지사항 조회
curl http://localhost:8000/api/announcements
```

## 프로젝트 구조

```
church-website/
├── main.py                 # FastAPI 메인 애플리케이션
├── church.db              # SQLite 데이터베이스 (자동 생성)
├── requirements.txt       # Python 패키지 목록
├── templates/
│   └── index.html        # 메인 HTML 템플릿
├── static/
│   ├── css/
│   │   └── style.css     # 스타일시트
│   ├── js/
│   │   └── script.js     # JavaScript
│   └── images/           # 이미지 파일 (필요시 추가)
└── README.md             # 프로젝트 설명서
```

## 데이터베이스 구조

### users (사용자)
- id: 고유 ID
- username: 사용자명
- password: 비밀번호 (SHA-256 해시)
- role: 권한 (admin/user)
- created_at: 생성일

### church_info (교회 정보)
- id: 고유 ID
- content: 교회 소개 내용
- updated_at: 수정일

### sermons (설교)
- id: 고유 ID
- title: 설교 제목
- pastor: 설교자
- date: 날짜
- description: 설명

### news (교회소식)
- id: 고유 ID
- title: 제목
- content: 내용
- date: 작성일
- views: 조회수
- author: 작성자
- image_path: 이미지 경로

## 로그인 정보

### 기본 관리자 계정
- **아이디**: admin
- **비밀번호**: 환경변수 ADMIN_PASSWORD로 설정 (기본값: changeme)

⚠️ **보안 주의**: 실제 운영 시 반드시 환경변수 ADMIN_PASSWORD를 설정하세요!

## 사용 방법

### 관리자 페이지 접속
1. 홈페이지 상단 "로그인" 클릭
2. 관리자 계정으로 로그인
3. 자동으로 관리자 대시보드로 이동

### 교회소식 작성
1. 관리자 페이지에서 "새 소식 작성" 섹션으로 이동
2. 제목과 내용 입력
3. 필요시 이미지 첨부 (선택사항)
4. "소식 등록" 버튼 클릭

### 교회 소개 수정
1. 관리자 페이지에서 "교회 소개 관리" 섹션으로 이동
2. 내용 수정
3. "저장" 버튼 클릭

## 커스터마이징

### 1. 교회 정보 수정

`templates/index.html` 파일에서 다음 내용을 수정하세요:
- 교회 이름: "더하는 교회"
- 소속: "기독교 한국침례회"
- 교회대표: "김한기 목사"
- 주소: "대전시 유성구 학하동 755-6 1층"
- 전화번호 (현재 042-XXX-XXXX로 표시됨)

### 1-1. 네이버 지도 API 설정 (선택사항)

네이버 지도를 실제로 표시하려면:
1. [네이버 클라우드 플랫폼](https://www.ncloud.com/)에서 Maps API 키 발급
2. `templates/index.html`의 `<script>` 태그에서 `YOUR_CLIENT_ID`를 발급받은 키로 교체
3. `static/js/script.js`의 좌표를 정확한 교회 위치로 수정

**참고**: API 키 없이도 "네이버 지도로 길찾기" 버튼은 정상 작동합니다.

### 2. 색상 테마 변경

`static/css/style.css` 파일의 `:root` 섹션에서 CSS 변수를 수정하세요:
- `--primary-color`: 주 색상
- `--secondary-color`: 보조 색상
- `--accent-color`: 강조 색상

### 3. 데이터 수정

애플리케이션이 처음 실행될 때 샘플 데이터가 자동으로 생성됩니다.
데이터를 수정하려면 `main.py`의 `init_db()` 함수를 수정하거나,
SQLite 클라이언트를 사용하여 `church.db` 파일을 직접 편집하세요.

## 배포

실제 서버에 배포할 때는 다음 사항을 고려하세요:

1. `uvicorn`을 프로덕션 모드로 실행
2. Nginx 또는 Apache를 리버스 프록시로 사용
3. HTTPS 인증서 설정
4. 환경 변수로 민감한 정보 관리

## 라이선스

이 프로젝트는 교회 사용을 위해 자유롭게 사용 및 수정할 수 있습니다.

## 문의

궁금한 사항이 있으시면 연락주세요.
# GitOps CI/CD Pipeline

This repository uses GitHub Actions and ArgoCD for automated deployments.
