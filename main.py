from fastapi import FastAPI, Request, Depends, HTTPException, Form, UploadFile, File, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib
import bcrypt
import secrets
import shutil
import re
from typing import Optional

app = FastAPI(title="더하는 교회")

# ─── i18n translations ───────────────────────────────────────────────
TRANSLATIONS = {
    "ko": {
        "lang": "ko",
        "lang_name": "한국어",
        "other_lang": "en",
        "other_lang_name": "English",
        "church_name": "더하는 교회",
        "church_name_full": "더하는 교회 - 기독교 한국침례회",
        "denomination": "기독교 한국침례회",
        "senior_pastor": "교회대표: 김한기 목사",
        "senior_pastor_short": "김한기 목사",
        "pastor_label": "담임목사: 김한기",
        # Navigation
        "nav_home": "홈",
        "nav_about": "교회소개",
        "nav_direction": "목회방향",
        "nav_vision": "비전과 가치",
        "nav_schedule": "예배시간 안내",
        "nav_location": "찾아오시는 길",
        "nav_people": "섬기는 분들",
        "nav_videos": "영상",
        "nav_church_vision": "교회 비전",
        "nav_sermons": "최근설교",
        "nav_shorts": "숏츠",
        "nav_qt": "오늘의 QT",
        "nav_pastoral": "목양의 窓",
        "nav_worship": "예배안내",
        "nav_news": "교회소식",
        "nav_admin": "관리자",
        "nav_logout": "로그아웃",
        "nav_login": "로그인",
        # Hero
        "hero_title": "하나님 나라와 의를 구하는 교회",
        "hero_subtitle": "더하는 교회에 오신 것을 환영합니다",
        "hero_info": "기독교 한국침례회 · 교회 대표 김한기 목사",
        "hero_worship_btn": "예배 안내",
        "hero_about_btn": "교회 소개",
        # Welcome
        "welcome_title": "환영합니다",
        "info_affiliation": "소속:",
        "info_pastor": "교회대표:",
        "info_location": "위치:",
        "info_location_val": "대전시 유성구 학하동",
        # Videos
        "tab_vision": "교회 비전",
        "tab_sermons": "최근설교",
        "tab_shorts": "숏츠",
        "tab_qt": "오늘의 QT",
        "prev_video": "이전영상",
        "next_video": "다음영상",
        # Schedule & News
        "schedule_title": "예배 시간 안내",
        "news_title": "교회소식",
        "sunday_worship": "주일 예배",
        "sunday_time": "일요일 오전 10:40",
        "sunday_study": "주일 성경공부 및 목장 모임",
        "sunday_study_time": "일요일 오후 1:00",
        "wed_worship": "수요 예배",
        "wed_time": "수요일 오후 7:30 (Zoom)",
        "fri_prayer": "금요 기도회",
        "fri_time": "금요일 오후 7:30",
        "morning_worship": "아침 예배",
        "morning_time": "오전 7:00 (Zoom)",
        "news_col_num": "번호",
        "news_col_title": "제목",
        "news_col_date": "작성일",
        "news_col_views": "조회",
        # Contact
        "contact_title": "찾아오시는 길",
        "naver_map": "네이버 지도로 길찾기",
        "kakao_map": "카카오맵으로 길찾기",
        # Footer
        "footer_address_label": "주소",
        "footer_address": "대전시 유성구 학하동 755-6 1층",
        "footer_tel": "Tel: 042-626-0291",
        "footer_copyright": "&copy; 2026 더하는 교회. All rights reserved.",
        "footer_blessing": "하나님의 사랑과 은혜가 함께 하시기를 기도합니다.",
        "footer_email": "이메일: muhan52@hanmail.net",
        "footer_phone": "전화: 042-626-0291",
        # About page
        "about_title": "교회소개",
        "mission_5_title": "교회의 5대 사명",
        # Direction page
        "direction_title": "목회방향",
        "direction_preparing": "준비 중입니다.",
        # People page
        "people_title": "섬기는 분들",
        "people_preparing": "준비 중입니다.",
        # Pastoral board
        "pastoral_title": "목양의 窓",
        "pastoral_subtitle": "말씀 나눔과 성도 간 교제의 장입니다",
        "pastoral_search_placeholder": "제목 또는 내용으로 검색...",
        "pastoral_search_btn": "검색",
        "pastoral_search_result": "검색 결과",
        "pastoral_all_list": "전체 목록",
        "pastoral_col_title": "제목",
        "pastoral_col_date": "날짜",
        "pastoral_col_author": "작성자",
        "pastoral_col_views": "조회",
        "pastoral_empty": "아직 게시글이 없습니다.",
        "pastoral_no_result": "에 대한 검색 결과가 없습니다.",
        "pastoral_prev": "&laquo; 이전",
        "pastoral_next": "다음 &raquo;",
        "pastoral_back": "&larr; 목록으로 돌아가기",
        "pastoral_author_label": "&#128221; 작성자:",
        "pastoral_date_label": "&#128197; 작성일:",
        "pastoral_views_label": "&#128065; 조회수:",
        "pastoral_default_author": "관리자",
        # Comments
        "comments_title": "댓글",
        "no_comments": "아직 댓글이 없습니다.",
        "comment_placeholder": "댓글을 입력하세요...",
        "comment_submit": "댓글 작성",
        "comment_login_prompt": "댓글을 작성하려면",
        "comment_login_link": "로그인",
        "comment_login_suffix": "해 주세요.",
        "comment_delete": "삭제",
        "comment_delete_confirm": "댓글을 삭제하시겠습니까?",
        # News detail
        "news_author_label": "작성자:",
        "news_date_label": "작성일:",
        "news_views_label": "조회수:",
        "news_back": "&larr; 목록으로 돌아가기",
        "news_default_author": "관리자",
        # Login
        "login_title": "로그인",
        "login_username": "아이디",
        "login_password": "비밀번호",
        "login_button": "로그인",
        "login_no_account": "계정이 없으신가요?",
        "login_register_link": "회원가입",
        "login_back": "&larr; 메인 페이지로 돌아가기",
        "login_error": "아이디 또는 비밀번호가 올바르지 않습니다.",
        # Register
        "register_title": "회원가입",
        "register_name": "이름",
        "register_email": "이메일",
        "register_username": "아이디",
        "register_password": "비밀번호",
        "register_password_confirm": "비밀번호 확인",
        "register_button": "회원가입",
        "register_has_account": "이미 계정이 있으신가요?",
        "register_login_link": "로그인",
        "register_back": "&larr; 메인 페이지로 돌아가기",
        "register_password_hint": "6자 이상",
        "register_success": "회원가입이 완료되었습니다. 로그인해 주세요.",
        # Validation errors
        "err_name_short": "이름은 2자 이상이어야 합니다.",
        "err_username_short": "아이디는 3자 이상이어야 합니다.",
        "err_password_short": "비밀번호는 6자 이상이어야 합니다.",
        "err_password_mismatch": "비밀번호가 일치하지 않습니다.",
        "err_email_invalid": "올바른 이메일 주소를 입력하세요.",
        "err_username_taken": "이미 사용 중인 아이디입니다.",
        "err_email_taken": "이미 사용 중인 이메일입니다.",
    },
    "en": {
        "lang": "en",
        "lang_name": "English",
        "other_lang": "ko",
        "other_lang_name": "한국어",
        "church_name": "Deohaneun Church",
        "church_name_full": "Deohaneun Church - Korea Baptist Convention",
        "denomination": "Korea Baptist Convention",
        "senior_pastor": "Senior Pastor: Rev. Hangi Kim",
        "senior_pastor_short": "Rev. Hangi Kim",
        "pastor_label": "Senior Pastor: Hangi Kim",
        # Navigation
        "nav_home": "Home",
        "nav_about": "About",
        "nav_direction": "Pastoral Direction",
        "nav_vision": "Vision & Values",
        "nav_schedule": "Worship Schedule",
        "nav_location": "Location",
        "nav_people": "Our Staff",
        "nav_videos": "Media",
        "nav_church_vision": "Church Vision",
        "nav_sermons": "Sermons",
        "nav_shorts": "Shorts",
        "nav_qt": "Daily QT",
        "nav_pastoral": "Pastoral Window",
        "nav_worship": "Worship Info",
        "nav_news": "Church News",
        "nav_admin": "Admin",
        "nav_logout": "Logout",
        "nav_login": "Login",
        # Hero
        "hero_title": "Seeking the Kingdom of God and His Righteousness",
        "hero_subtitle": "Welcome to Deohaneun Church",
        "hero_info": "Korea Baptist Convention · Senior Pastor Rev. Hangi Kim",
        "hero_worship_btn": "Worship Info",
        "hero_about_btn": "About Us",
        # Welcome
        "welcome_title": "Welcome",
        "info_affiliation": "Affiliation:",
        "info_pastor": "Senior Pastor:",
        "info_location": "Location:",
        "info_location_val": "Hakha-dong, Yuseong-gu, Daejeon",
        # Videos
        "tab_vision": "Church Vision",
        "tab_sermons": "Sermons",
        "tab_shorts": "Shorts",
        "tab_qt": "Daily QT",
        "prev_video": "Previous",
        "next_video": "Next",
        # Schedule & News
        "schedule_title": "Worship Schedule",
        "news_title": "Church News",
        "sunday_worship": "Sunday Worship",
        "sunday_time": "Sunday 10:40 AM",
        "sunday_study": "Sunday Bible Study & Small Group",
        "sunday_study_time": "Sunday 1:00 PM",
        "wed_worship": "Wednesday Worship",
        "wed_time": "Wednesday 7:30 PM (Zoom)",
        "fri_prayer": "Friday Prayer Meeting",
        "fri_time": "Friday 7:30 PM",
        "morning_worship": "Morning Worship",
        "morning_time": "7:00 AM (Zoom)",
        "news_col_num": "No.",
        "news_col_title": "Title",
        "news_col_date": "Date",
        "news_col_views": "Views",
        # Contact
        "contact_title": "Location & Directions",
        "naver_map": "Get Directions (Naver Map)",
        "kakao_map": "Get Directions (Kakao Map)",
        # Footer
        "footer_address_label": "Address",
        "footer_address": "755-6, Hakha-dong, Yuseong-gu, Daejeon, 1F",
        "footer_tel": "Tel: 042-626-0291",
        "footer_copyright": "&copy; 2026 Deohaneun Church. All rights reserved.",
        "footer_blessing": "May God's love and grace be with you.",
        "footer_email": "Email: muhan52@hanmail.net",
        "footer_phone": "Phone: 042-626-0291",
        # About page
        "about_title": "About Us",
        "mission_5_title": "Five Missions of the Church",
        # Direction page
        "direction_title": "Pastoral Direction",
        "direction_preparing": "Coming soon.",
        # People page
        "people_title": "Our Staff",
        "people_preparing": "Coming soon.",
        # Pastoral board
        "pastoral_title": "Pastoral Window",
        "pastoral_subtitle": "A place for sharing the Word and fellowship among believers",
        "pastoral_search_placeholder": "Search by title or content...",
        "pastoral_search_btn": "Search",
        "pastoral_search_result": "search results",
        "pastoral_all_list": "All Posts",
        "pastoral_col_title": "Title",
        "pastoral_col_date": "Date",
        "pastoral_col_author": "Author",
        "pastoral_col_views": "Views",
        "pastoral_empty": "No posts yet.",
        "pastoral_no_result": "No results found for",
        "pastoral_prev": "&laquo; Prev",
        "pastoral_next": "Next &raquo;",
        "pastoral_back": "&larr; Back to List",
        "pastoral_author_label": "&#128221; Author:",
        "pastoral_date_label": "&#128197; Date:",
        "pastoral_views_label": "&#128065; Views:",
        "pastoral_default_author": "Admin",
        # Comments
        "comments_title": "Comments",
        "no_comments": "No comments yet.",
        "comment_placeholder": "Write a comment...",
        "comment_submit": "Post Comment",
        "comment_login_prompt": "Please",
        "comment_login_link": "log in",
        "comment_login_suffix": "to write a comment.",
        "comment_delete": "Delete",
        "comment_delete_confirm": "Are you sure you want to delete this comment?",
        # News detail
        "news_author_label": "Author:",
        "news_date_label": "Date:",
        "news_views_label": "Views:",
        "news_back": "&larr; Back to List",
        "news_default_author": "Admin",
        # Login
        "login_title": "Login",
        "login_username": "Username",
        "login_password": "Password",
        "login_button": "Login",
        "login_no_account": "Don't have an account?",
        "login_register_link": "Sign Up",
        "login_back": "&larr; Back to Home",
        "login_error": "Invalid username or password.",
        # Register
        "register_title": "Sign Up",
        "register_name": "Full Name",
        "register_email": "Email",
        "register_username": "Username",
        "register_password": "Password",
        "register_password_confirm": "Confirm Password",
        "register_button": "Sign Up",
        "register_has_account": "Already have an account?",
        "register_login_link": "Login",
        "register_back": "&larr; Back to Home",
        "register_password_hint": "At least 6 characters",
        "register_success": "Registration successful. Please log in.",
        # Validation errors
        "err_name_short": "Name must be at least 2 characters.",
        "err_username_short": "Username must be at least 3 characters.",
        "err_password_short": "Password must be at least 6 characters.",
        "err_password_mismatch": "Passwords do not match.",
        "err_email_invalid": "Please enter a valid email address.",
        "err_username_taken": "This username is already taken.",
        "err_email_taken": "This email is already in use.",
    }
}

def get_t(lang: str = "ko") -> dict:
    """Get translation dict for given language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS["ko"])

def get_lang_prefix(lang: str) -> str:
    """Get URL prefix for language"""
    return "/en" if lang == "en" else ""

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

import os
DB_PATH = os.getenv("DB_PATH", "church.db")
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

security = HTTPBasic()

# Session storage (in production, use Redis or database)
sessions = {}

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except (ValueError, TypeError):
        return False

def is_sha256_hash(hashed: str) -> bool:
    """Check if a hash is legacy SHA-256 format (64 hex chars)"""
    return len(hashed) == 64 and all(c in '0123456789abcdef' for c in hashed)

def verify_sha256(password: str, hashed: str) -> bool:
    """Verify password against legacy SHA-256 hash"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def extract_youtube_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL (including Shorts and Live)"""
    import re
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]+)',  # Shorts support
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/live\/([a-zA-Z0-9_-]{11})'  # Live support
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def init_db():
    """Initialize the database with sample data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL
        )
    """)

    # Church info table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS church_info (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sermons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            pastor TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            youtube_url TEXT
        )
    """)

    # Migration: Add youtube_url column if it doesn't exist
    cursor.execute("PRAGMA table_info(sermons)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'youtube_url' not in columns:
        cursor.execute("ALTER TABLE sermons ADD COLUMN youtube_url TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            date TEXT NOT NULL,
            views INTEGER DEFAULT 0,
            author TEXT,
            image_path TEXT
        )
    """)

    # Vision table for YouTube videos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            youtube_url TEXT NOT NULL,
            date TEXT NOT NULL,
            author TEXT
        )
    """)

    # Shorts table for YouTube Shorts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shorts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            youtube_url TEXT NOT NULL,
            date TEXT NOT NULL,
            author TEXT
        )
    """)

    # QTY (오늘의 큐티) table for YouTube videos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qtys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            youtube_url TEXT NOT NULL,
            date TEXT NOT NULL,
            author TEXT
        )
    """)

    # 목양의 窓 (Pastoral Window) board
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pastoral_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            image_path TEXT,
            author TEXT,
            views INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    # Church About table for vision and missions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS church_about (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vision_title TEXT NOT NULL,
            vision_content TEXT NOT NULL,
            mission_content TEXT NOT NULL,
            pastoral_direction TEXT NOT NULL DEFAULT '',
            serving_people TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL
        )
    """)
    
    # Add new columns if they don't exist
    try:
        cursor.execute("ALTER TABLE church_about ADD COLUMN pastoral_direction TEXT NOT NULL DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE church_about ADD COLUMN serving_people TEXT NOT NULL DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    # Members table (섬기는 분들)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            bio TEXT NOT NULL DEFAULT '',
            photo_path TEXT,
            display_order INTEGER DEFAULT 0
        )
    """)

    # Comments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_type TEXT NOT NULL,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Migration: Add name and email columns to users table
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN name TEXT NOT NULL DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    # Check if admin exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    if cursor.fetchone()[0] == 0:
        # Create default admin (username: admin, password: CHANGE_THIS_PASSWORD)
        cursor.execute("""
            INSERT INTO users (username, password, role, created_at)
            VALUES (?, ?, 'admin', ?)
        """, ('admin', hash_password(os.getenv('ADMIN_PASSWORD', 'changeme')), datetime.now().isoformat()))

    # Check if church info exists
    cursor.execute("SELECT COUNT(*) FROM church_info")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO church_info (id, content, updated_at)
            VALUES (1, '더하는 교회는 하나님의 사랑과 예수 그리스도의 복음을 전하는 믿음의 공동체입니다.', ?)
        """, (datetime.now().isoformat(),))

    # Check if church about exists
    cursor.execute("SELECT COUNT(*) FROM church_about")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO church_about (id, vision_title, vision_content, mission_content, pastoral_direction, serving_people, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?)
        """, (
            "더하는교회의 비전",
            """더하는교회의 비전은 한 문장으로 말하면,
하나님과의 순전한 사귐과 누림을 통해 자라나
깨진 세상의 회복자로 살아가는 성도(하품사)를 세우는 것입니다.

1️⃣ 하나님과의 사귐과 누림
신앙의 출발은 활동이 아니라 관계라고 믿습니다.
하나님 나라를 먼저 대망하며 예배하고,
말씀과 큐티를 통해 하나님을 깊이 누리는 삶을 중요하게 여깁니다.

2️⃣ 함께 자라가는 공동체
혼자 성장하는 신앙이 아니라,
하늘 가족으로서 삶을 나누며
그리스도의 장성한 분량까지 함께 자라가는 공동체를 지향합니다.
교회의 목표는 결국 잃어버렸던 그리스도의 형상을 닮는 것입니다.

3️⃣ 깨진 세상의 회복자
성도는 교회 안에 머무는 사람이 아니라,
세상으로 보냄 받은 선교사입니다.
하나님을 떠난 자들을 찾아 복음을 나누고,
깨진 세상을 섬기며 변화를 이루는 삶으로 나아갑니다.""",
            """하나님 나라를 대망하며 함께 예배하고 (예배)
진솔한 하늘 가족 공동체로 함께 삶을 나누고 (교제)
균형 잡힌 신앙의 성숙을 함께 이루며 (교육)
하나님을 떠난 자들과 복음을 나누고 (전도)
깨진 세상의 변혁을 함께 이루어 갑니다 (봉사)""",
            "",
            "",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM sermons")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO sermons (title, pastor, date, description, youtube_url)
            VALUES
            ('머리 잃은 세상에 머리로 오신 예수님', '김한기 목사', '2026-02-16', '머리 잃은 세상에 머리로 오신 예수님', 'https://www.youtube.com/live/2yjRBwmC28I?si=HVsv8BXBVOyy9XIJ'),
            ('숨지 않는 사람을 찾으시는 하나님', '김한기 목사', '2026-02-16', '숨지 않는 사람을 찾으시는 하나님', 'https://www.youtube.com/live/I8WezzbVDi4?si=0qsVyq3byvm-4f7P')
        """)

        cursor.execute("""
            INSERT INTO news (title, content, date, views, author)
            VALUES
            ('새가족 환영', '이번 주 새로 오신 가족분들을 진심으로 환영합니다. 예배 후 1층 카페에서 새가족 환영회가 있습니다.', '2026-02-16', 0, '관리자'),
            ('성경공부 개강', '3월부터 새로운 성경공부 과정이 시작됩니다. 신청은 교육부로 연락 주시기 바랍니다.', '2026-02-15', 0, '관리자'),
            ('찬양예배 안내', '이번 주 수요일 저녁 7시, 특별 찬양예배가 있습니다. 많은 참여 부탁드립니다.', '2026-02-14', 0, '관리자')
        """)

        cursor.execute("""
            INSERT INTO visions (title, youtube_url, date, author)
            VALUES
            ('더하는 교회 비전', 'https://youtu.be/p1H6GPhqE-U?si=YzYgySlrIRbgCFDz', '2026-02-16', 'admin')
        """)

        cursor.execute("""
            INSERT INTO shorts (title, youtube_url, date, author)
            VALUES
            ('요엘', 'https://youtube.com/shorts/pwBEmlFKc2g?si=dVuAYcN2oMgGlXVH', '2026-02-16', 'admin')
        """)

    conn.commit()
    conn.close()

def get_current_user(request: Request) -> Optional[dict]:
    """Get current logged in user from session"""
    session_token = request.cookies.get("session_token")
    if session_token and session_token in sessions:
        return sessions[session_token]
    return None

def require_admin(request: Request):
    """Require admin role"""
    user = get_current_user(request)
    if not user or user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@app.on_event("startup")
async def startup_event():
    init_db()

async def _home(request: Request, lang: str = "ko"):
    """Main homepage (shared logic)"""
    t = get_t(lang)
    lp = get_lang_prefix(lang)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT content FROM church_info WHERE id=1")
    result = cursor.fetchone()
    church_intro = result[0] if result else "더하는 교회는 하나님의 사랑과 예수 그리스도의 복음을 전하는 믿음의 공동체입니다."

    cursor.execute("SELECT * FROM visions ORDER BY date DESC LIMIT 5")
    visions = []
    for row in cursor.fetchall():
        video_id = extract_youtube_id(row[2])
        visions.append({
            "id": row[0], "title": row[1], "youtube_url": row[2], "youtube_id": video_id,
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg" if video_id else None,
            "date": row[3], "author": row[4] if len(row) > 4 else None
        })

    cursor.execute("SELECT * FROM sermons ORDER BY date DESC LIMIT 5")
    sermons = []
    for row in cursor.fetchall():
        video_id = extract_youtube_id(row[5]) if len(row) > 5 and row[5] else None
        sermons.append({
            "id": row[0], "title": row[1], "pastor": row[2], "date": row[3],
            "description": row[4], "youtube_url": row[5] if len(row) > 5 else None,
            "youtube_id": video_id,
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg" if video_id else None
        })

    cursor.execute("SELECT * FROM shorts ORDER BY date DESC LIMIT 10")
    shorts = []
    for row in cursor.fetchall():
        video_id = extract_youtube_id(row[2])
        shorts.append({
            "id": row[0], "title": row[1], "youtube_url": row[2], "youtube_id": video_id,
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg" if video_id else None,
            "date": row[3], "author": row[4] if len(row) > 4 else None
        })

    cursor.execute("SELECT * FROM qtys ORDER BY date DESC LIMIT 10")
    qtys = []
    for row in cursor.fetchall():
        video_id = extract_youtube_id(row[2])
        qtys.append({
            "id": row[0], "title": row[1], "youtube_url": row[2], "youtube_id": video_id,
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg" if video_id else None,
            "date": row[3], "author": row[4] if len(row) > 4 else None
        })

    cursor.execute("SELECT * FROM news ORDER BY date DESC LIMIT 5")
    news_list = [{"id": row[0], "title": row[1], "content": row[2], "date": row[3], "views": row[4], "author": row[5], "image_path": row[6]}
                for row in cursor.fetchall()]

    conn.close()
    user = get_current_user(request)

    return templates.TemplateResponse("index.html", {
        "request": request, "t": t, "lp": lp,
        "visions": visions, "sermons": sermons, "shorts": shorts,
        "qtys": qtys, "news_list": news_list,
        "church_intro": church_intro, "user": user
    })

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return await _home(request, "ko")

@app.get("/en/", response_class=HTMLResponse)
async def home_en(request: Request):
    return await _home(request, "en")

async def _about_page(request: Request, lang: str = "ko"):
    t = get_t(lang)
    lp = get_lang_prefix(lang)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT vision_title, vision_content, mission_content, pastoral_direction, serving_people FROM church_about WHERE id=1")
    row = cursor.fetchone()
    conn.close()
    about = {
        "vision_title": row[0] if row else "더하는교회의 비전",
        "vision_content": row[1] if row else "",
        "mission_content": row[2] if row else "",
        "pastoral_direction": row[3] if row else "",
        "serving_people": row[4] if row else ""
    }
    return templates.TemplateResponse("about.html", {"request": request, "about": about, "t": t, "lp": lp})

@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return await _about_page(request, "ko")

@app.get("/en/about", response_class=HTMLResponse)
async def about_page_en(request: Request):
    return await _about_page(request, "en")

async def _direction_page(request: Request, lang: str = "ko"):
    t = get_t(lang)
    lp = get_lang_prefix(lang)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT pastoral_direction FROM church_about WHERE id=1")
    row = cursor.fetchone()
    conn.close()
    content = row[0] if row and row[0] else t["direction_preparing"]
    return templates.TemplateResponse("direction.html", {"request": request, "content": content, "t": t, "lp": lp})

@app.get("/direction", response_class=HTMLResponse)
async def direction_page(request: Request):
    return await _direction_page(request, "ko")

@app.get("/en/direction", response_class=HTMLResponse)
async def direction_page_en(request: Request):
    return await _direction_page(request, "en")

async def _people_page(request: Request, lang: str = "ko"):
    t = get_t(lang)
    lp = get_lang_prefix(lang)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members ORDER BY display_order ASC, id ASC")
    members = [{"id": row[0], "name": row[1], "role": row[2], "bio": row[3],
                "photo_path": row[4], "display_order": row[5]}
               for row in cursor.fetchall()]
    cursor.execute("SELECT serving_people FROM church_about WHERE id=1")
    row = cursor.fetchone()
    intro = row[0] if row and row[0] else ""
    conn.close()
    return templates.TemplateResponse("people.html", {"request": request, "members": members, "intro": intro, "t": t, "lp": lp})

@app.get("/people", response_class=HTMLResponse)
async def people_page(request: Request):
    return await _people_page(request, "ko")

@app.get("/en/people", response_class=HTMLResponse)
async def people_page_en(request: Request):
    return await _people_page(request, "en")

async def _pastoral_list(request: Request, lang: str = "ko", page: int = 1, q: str = ""):
    t = get_t(lang)
    lp = get_lang_prefix(lang)
    per_page = 20
    offset = (page - 1) * per_page
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if q.strip():
        search = f"%{q.strip()}%"
        cursor.execute("SELECT COUNT(*) FROM pastoral_posts WHERE title LIKE ? OR content LIKE ?", (search, search))
        total = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM pastoral_posts WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                        (search, search, per_page, offset))
    else:
        cursor.execute("SELECT COUNT(*) FROM pastoral_posts")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM pastoral_posts ORDER BY created_at DESC LIMIT ? OFFSET ?", (per_page, offset))
    posts = [{"id": row[0], "title": row[1], "content": row[2], "image_path": row[3],
              "author": row[4], "views": row[5], "created_at": row[6]}
             for row in cursor.fetchall()]
    conn.close()
    total_pages = max(1, (total + per_page - 1) // per_page)
    user = get_current_user(request)
    return templates.TemplateResponse("pastoral_list.html", {
        "request": request, "posts": posts, "user": user, "t": t, "lp": lp,
        "page": page, "total_pages": total_pages, "total": total, "q": q
    })

@app.get("/pastoral", response_class=HTMLResponse)
async def pastoral_list(request: Request, page: int = 1, q: str = ""):
    return await _pastoral_list(request, "ko", page, q)

@app.get("/en/pastoral", response_class=HTMLResponse)
async def pastoral_list_en(request: Request, page: int = 1, q: str = ""):
    return await _pastoral_list(request, "en", page, q)

async def _pastoral_detail(request: Request, post_id: int, lang: str = "ko"):
    t = get_t(lang)
    lp = get_lang_prefix(lang)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE pastoral_posts SET views = views + 1 WHERE id=?", (post_id,))
    conn.commit()
    cursor.execute("SELECT * FROM pastoral_posts WHERE id=?", (post_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Post not found")
    post = {"id": row[0], "title": row[1], "content": row[2], "image_path": row[3],
            "author": row[4], "views": row[5], "created_at": row[6]}
    cursor.execute("""
        SELECT c.id, c.content, c.created_at, u.username, u.name, c.user_id
        FROM comments c JOIN users u ON c.user_id = u.id
        WHERE c.post_type='pastoral' AND c.post_id=?
        ORDER BY c.created_at ASC
    """, (post_id,))
    comments = [{"id": r[0], "content": r[1], "created_at": r[2],
                 "username": r[3], "name": r[4], "user_id": r[5]}
                for r in cursor.fetchall()]
    conn.close()
    user = get_current_user(request)
    return templates.TemplateResponse("pastoral_detail.html", {
        "request": request, "post": post, "comments": comments, "user": user, "t": t, "lp": lp
    })

@app.get("/pastoral/{post_id}", response_class=HTMLResponse)
async def pastoral_detail(request: Request, post_id: int):
    return await _pastoral_detail(request, post_id, "ko")

@app.get("/en/pastoral/{post_id}", response_class=HTMLResponse)
async def pastoral_detail_en(request: Request, post_id: int):
    return await _pastoral_detail(request, post_id, "en")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    t = get_t("ko")
    return templates.TemplateResponse("login.html", {"request": request, "t": t, "lp": ""})

@app.get("/en/login", response_class=HTMLResponse)
async def login_page_en(request: Request):
    t = get_t("en")
    return templates.TemplateResponse("login.html", {"request": request, "t": t, "lp": "/en"})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    t = get_t("ko")
    return templates.TemplateResponse("register.html", {"request": request, "t": t, "lp": ""})

@app.get("/en/register", response_class=HTMLResponse)
async def register_page_en(request: Request):
    t = get_t("en")
    return templates.TemplateResponse("register.html", {"request": request, "t": t, "lp": "/en"})

async def _register_post(request: Request, lang: str, name: str, email: str, username: str, password: str, password_confirm: str):
    t = get_t(lang)
    lp = get_lang_prefix(lang)
    errors = []
    if len(name.strip()) < 2:
        errors.append(t["err_name_short"])
    if len(username.strip()) < 3:
        errors.append(t["err_username_short"])
    if len(password) < 6:
        errors.append(t["err_password_short"])
    if password != password_confirm:
        errors.append(t["err_password_mismatch"])
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        errors.append(t["err_email_invalid"])
    if errors:
        return templates.TemplateResponse("register.html", {
            "request": request, "errors": errors, "t": t, "lp": lp,
            "name": name, "email": email, "username": username
        })
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return templates.TemplateResponse("register.html", {
            "request": request, "errors": [t["err_username_taken"]], "t": t, "lp": lp,
            "name": name, "email": email, "username": username
        })
    cursor.execute("SELECT id FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        conn.close()
        return templates.TemplateResponse("register.html", {
            "request": request, "errors": [t["err_email_taken"]], "t": t, "lp": lp,
            "name": name, "email": email, "username": username
        })
    hashed = hash_password(password)
    cursor.execute("""
        INSERT INTO users (username, password, role, created_at, name, email)
        VALUES (?, ?, 'user', ?, ?, ?)
    """, (username, hashed, datetime.now().isoformat(), name.strip(), email))
    conn.commit()
    conn.close()
    return templates.TemplateResponse("login.html", {
        "request": request, "t": t, "lp": lp,
        "success": t["register_success"]
    })

@app.post("/register")
async def register(request: Request, name: str = Form(...), email: str = Form(...),
                   username: str = Form(...), password: str = Form(...), password_confirm: str = Form(...)):
    return await _register_post(request, "ko", name, email, username, password, password_confirm)

@app.post("/en/register")
async def register_en(request: Request, name: str = Form(...), email: str = Form(...),
                      username: str = Form(...), password: str = Form(...), password_confirm: str = Form(...)):
    return await _register_post(request, "en", name, email, username, password, password_confirm)

async def _login_post(request: Request, lang: str, username: str, password: str):
    t = get_t(lang)
    lp = get_lang_prefix(lang)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return templates.TemplateResponse("login.html", {"request": request, "error": t["login_error"], "t": t, "lp": lp})
    stored_hash = user[2]
    password_valid = False
    if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$'):
        password_valid = verify_password(password, stored_hash)
    elif is_sha256_hash(stored_hash) and verify_sha256(password, stored_hash):
        password_valid = True
        new_hash = hash_password(password)
        cursor.execute("UPDATE users SET password=? WHERE id=?", (new_hash, user[0]))
        conn.commit()
    if not password_valid:
        conn.close()
        return templates.TemplateResponse("login.html", {"request": request, "error": t["login_error"], "t": t, "lp": lp})
    session_token = secrets.token_urlsafe(32)
    sessions[session_token] = {"id": user[0], "username": user[1], "role": user[3]}
    conn.close()
    response = RedirectResponse(url="/admin" if user[3] == "admin" else f"{lp}/", status_code=303)
    response.set_cookie(key="session_token", value=session_token, httponly=True)
    return response

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    return await _login_post(request, "ko", username, password)

@app.post("/en/login")
async def login_en(request: Request, username: str = Form(...), password: str = Form(...)):
    return await _login_post(request, "en", username, password)

@app.get("/logout")
async def logout(request: Request):
    """Handle logout"""
    session_token = request.cookies.get("session_token")
    if session_token and session_token in sessions:
        del sessions[session_token]

    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_token")
    return response

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, user: dict = Depends(require_admin)):
    """Admin dashboard"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all visions
    cursor.execute("SELECT * FROM visions ORDER BY date DESC")
    visions = []
    for row in cursor.fetchall():
        video_id = extract_youtube_id(row[2])
        visions.append({
            "id": row[0],
            "title": row[1],
            "youtube_url": row[2],
            "youtube_id": video_id,
            "date": row[3],
            "author": row[4] if len(row) > 4 else None
        })

    # Get all sermons
    cursor.execute("SELECT * FROM sermons ORDER BY date DESC")
    sermons = []
    for row in cursor.fetchall():
        video_id = extract_youtube_id(row[5]) if len(row) > 5 and row[5] else None
        sermons.append({
            "id": row[0],
            "title": row[1],
            "pastor": row[2],
            "date": row[3],
            "description": row[4],
            "youtube_url": row[5] if len(row) > 5 else None,
            "youtube_id": video_id
        })

    # Get all shorts
    cursor.execute("SELECT * FROM shorts ORDER BY date DESC")
    shorts = []
    for row in cursor.fetchall():
        video_id = extract_youtube_id(row[2])
        shorts.append({
            "id": row[0],
            "title": row[1],
            "youtube_url": row[2],
            "youtube_id": video_id,
            "date": row[3],
            "author": row[4] if len(row) > 4 else None
        })

    # Get all QTY (오늘의 큐티)
    cursor.execute("SELECT * FROM qtys ORDER BY date DESC")
    qtys = []
    for row in cursor.fetchall():
        video_id = extract_youtube_id(row[2])
        qtys.append({
            "id": row[0],
            "title": row[1],
            "youtube_url": row[2],
            "youtube_id": video_id,
            "date": row[3],
            "author": row[4] if len(row) > 4 else None
        })

    # Get all news
    cursor.execute("SELECT * FROM news ORDER BY date DESC")
    news_list = [{"id": row[0], "title": row[1], "content": row[2], "date": row[3], "views": row[4], "author": row[5], "image_path": row[6]}
                for row in cursor.fetchall()]

    # Get church info
    cursor.execute("SELECT content FROM church_info WHERE id=1")
    result = cursor.fetchone()
    church_intro = result[0] if result else ""

    # Get church about content
    cursor.execute("SELECT vision_title, vision_content, mission_content, pastoral_direction, serving_people FROM church_about WHERE id=1")
    about_row = cursor.fetchone()
    about = {
        "vision_title": about_row[0] if about_row else "",
        "vision_content": about_row[1] if about_row else "",
        "mission_content": about_row[2] if about_row else "",
        "pastoral_direction": about_row[3] if about_row else "",
        "serving_people": about_row[4] if about_row else ""
    }

    # Get all pastoral posts (목양의 窓)
    cursor.execute("SELECT * FROM pastoral_posts ORDER BY created_at DESC")
    pastoral_posts = [{"id": row[0], "title": row[1], "content": row[2], "image_path": row[3],
                       "author": row[4], "views": row[5], "created_at": row[6]}
                      for row in cursor.fetchall()]

    # Get all members (섬기는 분들)
    cursor.execute("SELECT * FROM members ORDER BY display_order ASC, id ASC")
    members = [{"id": row[0], "name": row[1], "role": row[2], "bio": row[3],
                "photo_path": row[4], "display_order": row[5]}
               for row in cursor.fetchall()]

    conn.close()

    t = get_t("ko")
    return templates.TemplateResponse("admin.html", {
        "request": request, "t": t, "lp": "",
        "user": user,
        "visions": visions,
        "sermons": sermons,
        "shorts": shorts,
        "qtys": qtys,
        "news_list": news_list,
        "church_intro": church_intro,
        "about": about,
        "pastoral_posts": pastoral_posts,
        "members": members
    })

@app.post("/admin/news/create")
async def create_news(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    user: dict = Depends(require_admin)
):
    """Create new news post"""
    image_path = None

    if image and image.filename:
        # Save uploaded image
        file_extension = Path(image.filename).suffix
        filename = f"{datetime.now().timestamp()}{file_extension}"
        file_path = UPLOAD_DIR / filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_path = f"/uploads/{filename}"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO news (title, content, date, views, author, image_path)
        VALUES (?, ?, ?, 0, ?, ?)
    """, (title, content, datetime.now().strftime("%Y-%m-%d"), user['username'], image_path))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/news/delete/{news_id}")
async def delete_news(news_id: int, user: dict = Depends(require_admin)):
    """Delete news post"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM news WHERE id=?", (news_id,))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/church-info/update")
async def update_church_info(
    request: Request,
    content: str = Form(...),
    user: dict = Depends(require_admin)
):
    """Update church introduction"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE church_info SET content=?, updated_at=? WHERE id=1
    """, (content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/vision/create")
async def create_vision(
    title: str = Form(...),
    youtube_url: str = Form(...),
    user: dict = Depends(require_admin)
):
    """Create new vision post"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO visions (title, youtube_url, date, author)
        VALUES (?, ?, ?, ?)
    """, (title, youtube_url, datetime.now().strftime("%Y-%m-%d"), user['username']))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/vision/delete/{vision_id}")
async def delete_vision(vision_id: int, user: dict = Depends(require_admin)):
    """Delete vision post"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM visions WHERE id=?", (vision_id,))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/sermon/create")
async def create_sermon(
    title: str = Form(...),
    pastor: str = Form(...),
    description: str = Form(...),
    youtube_url: Optional[str] = Form(None),
    user: dict = Depends(require_admin)
):
    """Create new sermon"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sermons (title, pastor, date, description, youtube_url)
        VALUES (?, ?, ?, ?, ?)
    """, (title, pastor, datetime.now().strftime("%Y-%m-%d"), description, youtube_url))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/sermon/delete/{sermon_id}")
async def delete_sermon(sermon_id: int, user: dict = Depends(require_admin)):
    """Delete sermon"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sermons WHERE id=?", (sermon_id,))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/sermon/update/{sermon_id}")
async def update_sermon(
    sermon_id: int,
    title: str = Form(...),
    pastor: str = Form(...),
    date: str = Form(...),
    description: str = Form(...),
    youtube_url: Optional[str] = Form(None),
    user: dict = Depends(require_admin)
):
    """Update existing sermon"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sermons
        SET title=?, pastor=?, date=?, description=?, youtube_url=?
        WHERE id=?
    """, (title, pastor, date, description, youtube_url, sermon_id))

    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/member/create")
async def create_member(
    request: Request,
    name: str = Form(...),
    role: str = Form(...),
    bio: str = Form(''),
    display_order: int = Form(0),
    photo: Optional[UploadFile] = File(None),
    user: dict = Depends(require_admin)
):
    """Create new member"""
    photo_path = None
    if photo and photo.filename:
        file_extension = Path(photo.filename).suffix
        filename = f"member_{datetime.now().timestamp()}{file_extension}"
        file_path = UPLOAD_DIR / filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        photo_path = f"/uploads/{filename}"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO members (name, role, bio, photo_path, display_order)
        VALUES (?, ?, ?, ?, ?)
    """, (name, role, bio, photo_path, display_order))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/member/delete/{member_id}")
async def delete_member(member_id: int, user: dict = Depends(require_admin)):
    """Delete a member"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/about/update")
async def update_about(
    vision_title: str = Form(...),
    vision_content: str = Form(...),
    mission_content: str = Form(...),
    pastoral_direction: str = Form(''),
    serving_people: str = Form(''),
    user: dict = Depends(require_admin)
):
    """Update church about content"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE church_about
        SET vision_title=?, vision_content=?, mission_content=?, pastoral_direction=?, serving_people=?, updated_at=?
        WHERE id=1
    """, (vision_title, vision_content, mission_content, pastoral_direction, serving_people,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/shorts/create")
async def create_shorts(
    title: str = Form(...),
    youtube_url: str = Form(...),
    user: dict = Depends(require_admin)
):
    """Create new YouTube short"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO shorts (title, youtube_url, date, author)
        VALUES (?, ?, ?, ?)
    """, (title, youtube_url, datetime.now().strftime("%Y-%m-%d"), user['username']))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/shorts/delete/{shorts_id}")
async def delete_shorts(shorts_id: int, user: dict = Depends(require_admin)):
    """Delete a YouTube short"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shorts WHERE id = ?", (shorts_id,))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/shorts/update/{shorts_id}")
async def update_shorts(
    shorts_id: int,
    title: str = Form(...),
    youtube_url: str = Form(...),
    date: str = Form(...),
    user: dict = Depends(require_admin)
):
    """Update existing YouTube short"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE shorts SET title=?, youtube_url=?, date=? WHERE id=?
    """, (title, youtube_url, date, shorts_id))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/qty/create")
async def create_qty(
    title: str = Form(...),
    youtube_url: str = Form(...),
    user: dict = Depends(require_admin)
):
    """Create new QTY (오늘의 큐티)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO qtys (title, youtube_url, date, author)
        VALUES (?, ?, ?, ?)
    """, (title, youtube_url, datetime.now().strftime("%Y-%m-%d"), user['username']))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/qty/delete/{qty_id}")
async def delete_qty(qty_id: int, user: dict = Depends(require_admin)):
    """Delete a QTY"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM qtys WHERE id = ?", (qty_id,))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/qty/update/{qty_id}")
async def update_qty(
    qty_id: int,
    title: str = Form(...),
    youtube_url: str = Form(...),
    date: str = Form(...),
    user: dict = Depends(require_admin)
):
    """Update existing QTY"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE qtys SET title=?, youtube_url=?, date=? WHERE id=?
    """, (title, youtube_url, date, qty_id))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/upload-image")
async def upload_image(
    request: Request,
    image: UploadFile = File(...),
    user: dict = Depends(require_admin)
):
    """Upload image and return URL (for rich editor)"""
    if not image.filename:
        return JSONResponse({"error": "No file"}, status_code=400)

    file_extension = Path(image.filename).suffix.lower()
    if file_extension not in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
        return JSONResponse({"error": "지원하지 않는 파일 형식입니다."}, status_code=400)

    filename = f"content_{datetime.now().timestamp()}{file_extension}"
    file_path = UPLOAD_DIR / filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return JSONResponse({"url": f"/uploads/{filename}"})

def extract_first_image_from_content(content: str) -> Optional[str]:
    """Extract first <img> src from HTML content"""
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    return match.group(1) if match else None

@app.post("/admin/pastoral/create")
async def create_pastoral(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    user: dict = Depends(require_admin)
):
    """Create new pastoral post"""
    image_path = None
    if image and image.filename:
        file_extension = Path(image.filename).suffix
        filename = f"pastoral_{datetime.now().timestamp()}{file_extension}"
        file_path = UPLOAD_DIR / filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_path = f"/uploads/{filename}"

    # Auto-extract thumbnail from content if no image uploaded
    if not image_path:
        first_img = extract_first_image_from_content(content)
        if first_img:
            image_path = first_img
        else:
            image_path = "/static/images/logo.png"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pastoral_posts (title, content, image_path, author, views, created_at)
        VALUES (?, ?, ?, ?, 0, ?)
    """, (title, content, image_path, user['username'], datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/pastoral/update/{post_id}")
async def update_pastoral(
    request: Request,
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    user: dict = Depends(require_admin)
):
    """Update existing pastoral post"""
    image_path = None
    if image and image.filename:
        file_extension = Path(image.filename).suffix
        filename = f"pastoral_{datetime.now().timestamp()}{file_extension}"
        file_path = UPLOAD_DIR / filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_path = f"/uploads/{filename}"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if image_path:
        cursor.execute("UPDATE pastoral_posts SET title=?, content=?, image_path=? WHERE id=?",
                        (title, content, image_path, post_id))
    else:
        # Auto-extract thumbnail from content
        first_img = extract_first_image_from_content(content)
        if first_img:
            cursor.execute("UPDATE pastoral_posts SET title=?, content=?, image_path=? WHERE id=?",
                            (title, content, first_img, post_id))
        else:
            cursor.execute("UPDATE pastoral_posts SET title=?, content=? WHERE id=?",
                            (title, content, post_id))

    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/pastoral/delete/{post_id}")
async def delete_pastoral(post_id: int, user: dict = Depends(require_admin)):
    """Delete a pastoral post"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pastoral_posts WHERE id = ?", (post_id,))
    cursor.execute("DELETE FROM comments WHERE post_type='pastoral' AND post_id=?", (post_id,))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)

async def _view_news(request: Request, news_id: int, lang: str = "ko"):
    t = get_t(lang)
    lp = get_lang_prefix(lang)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE news SET views = views + 1 WHERE id=?", (news_id,))
    conn.commit()
    cursor.execute("SELECT * FROM news WHERE id=?", (news_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Post not found")
    news = {"id": row[0], "title": row[1], "content": row[2], "date": row[3], "views": row[4], "author": row[5], "image_path": row[6]}
    cursor.execute("""
        SELECT c.id, c.content, c.created_at, u.username, u.name, c.user_id
        FROM comments c JOIN users u ON c.user_id = u.id
        WHERE c.post_type='news' AND c.post_id=?
        ORDER BY c.created_at ASC
    """, (news_id,))
    comments = [{"id": r[0], "content": r[1], "created_at": r[2],
                 "username": r[3], "name": r[4], "user_id": r[5]}
                for r in cursor.fetchall()]
    conn.close()
    user = get_current_user(request)
    return templates.TemplateResponse("news_detail.html", {
        "request": request, "news": news, "comments": comments, "user": user, "t": t, "lp": lp
    })

@app.get("/news/{news_id}", response_class=HTMLResponse)
async def view_news(request: Request, news_id: int):
    return await _view_news(request, news_id, "ko")

@app.get("/en/news/{news_id}", response_class=HTMLResponse)
async def view_news_en(request: Request, news_id: int):
    return await _view_news(request, news_id, "en")

@app.post("/news/{news_id}/comment")
async def create_news_comment(request: Request, news_id: int, content: str = Form(...)):
    """Add comment to news article (logged-in users only)"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    if not content.strip():
        return RedirectResponse(url=f"/news/{news_id}", status_code=303)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO comments (post_type, post_id, user_id, content, created_at)
        VALUES ('news', ?, ?, ?, ?)
    """, (news_id, user['id'], content.strip(), datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return RedirectResponse(url=f"/news/{news_id}", status_code=303)

@app.post("/pastoral/{post_id}/comment")
async def create_pastoral_comment(request: Request, post_id: int, content: str = Form(...)):
    """Add comment to pastoral post (logged-in users only)"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    if not content.strip():
        return RedirectResponse(url=f"/pastoral/{post_id}", status_code=303)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO comments (post_type, post_id, user_id, content, created_at)
        VALUES ('pastoral', ?, ?, ?, ?)
    """, (post_id, user['id'], content.strip(), datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return RedirectResponse(url=f"/pastoral/{post_id}", status_code=303)

@app.post("/comment/{comment_id}/delete")
async def delete_comment(request: Request, comment_id: int, redirect: str = "/"):
    """Delete a comment (owner or admin only)"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM comments WHERE id=?", (comment_id,))
    comment = cursor.fetchone()
    if not comment:
        conn.close()
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

    if comment[0] != user['id'] and user['role'] != 'admin':
        conn.close()
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

    cursor.execute("DELETE FROM comments WHERE id=?", (comment_id,))
    conn.commit()
    conn.close()

    return RedirectResponse(url=redirect, status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
