from fastapi import FastAPI, Request, Depends, HTTPException, Form, UploadFile, File, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib
import secrets
import shutil
from typing import Optional

app = FastAPI(title="더하는 교회")

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
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

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

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main homepage"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get church info
    cursor.execute("SELECT content FROM church_info WHERE id=1")
    result = cursor.fetchone()
    church_intro = result[0] if result else "더하는 교회는 하나님의 사랑과 예수 그리스도의 복음을 전하는 믿음의 공동체입니다."

    # Get latest visions
    cursor.execute("SELECT * FROM visions ORDER BY date DESC LIMIT 5")
    visions = []
    for row in cursor.fetchall():
        video_id = extract_youtube_id(row[2])
        visions.append({
            "id": row[0],
            "title": row[1],
            "youtube_url": row[2],
            "youtube_id": video_id,
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg" if video_id else None,
            "date": row[3],
            "author": row[4] if len(row) > 4 else None
        })

    # Get latest sermons
    cursor.execute("SELECT * FROM sermons ORDER BY date DESC LIMIT 5")
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
            "youtube_id": video_id,
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg" if video_id else None
        })

    # Get latest YouTube Shorts
    cursor.execute("SELECT * FROM shorts ORDER BY date DESC LIMIT 10")
    shorts = []
    for row in cursor.fetchall():
        video_id = extract_youtube_id(row[2])
        shorts.append({
            "id": row[0],
            "title": row[1],
            "youtube_url": row[2],
            "youtube_id": video_id,
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg" if video_id else None,
            "date": row[3],
            "author": row[4] if len(row) > 4 else None
        })

    # Get latest QTY (오늘의 큐티)
    cursor.execute("SELECT * FROM qtys ORDER BY date DESC LIMIT 10")
    qtys = []
    for row in cursor.fetchall():
        video_id = extract_youtube_id(row[2])
        qtys.append({
            "id": row[0],
            "title": row[1],
            "youtube_url": row[2],
            "youtube_id": video_id,
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg" if video_id else None,
            "date": row[3],
            "author": row[4] if len(row) > 4 else None
        })

    # Get latest news
    cursor.execute("SELECT * FROM news ORDER BY date DESC LIMIT 5")
    news_list = [{"id": row[0], "title": row[1], "content": row[2], "date": row[3], "views": row[4], "author": row[5], "image_path": row[6]}
                for row in cursor.fetchall()]

    conn.close()

    user = get_current_user(request)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "visions": visions,
        "sermons": sermons,
        "shorts": shorts,
        "qtys": qtys,
        "news_list": news_list,
        "church_intro": church_intro,
        "user": user
    })

@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """Display church about page"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM church_about WHERE id=1")
    row = cursor.fetchone()
    conn.close()

    about = {
        "vision_title": row[1] if row else "더하는교회의 비전",
        "vision_content": row[2] if row else "",
        "mission_content": row[3] if row else "",
        "pastoral_direction": row[4] if len(row) > 4 else "",
        "serving_people": row[5] if len(row) > 5 else ""
    }

    return templates.TemplateResponse("about.html", {
        "request": request,
        "about": about
    })

@app.get("/direction", response_class=HTMLResponse)
async def direction_page(request: Request):
    """Pastoral Direction page"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT pastoral_direction FROM church_about WHERE id=1")
    row = cursor.fetchone()
    conn.close()

    content = row[0] if row and row[0] else "준비 중입니다."

    return templates.TemplateResponse("direction.html", {
        "request": request,
        "content": content
    })

@app.get("/people", response_class=HTMLResponse)
async def people_page(request: Request):
    """Serving People page"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT serving_people FROM church_about WHERE id=1")
    row = cursor.fetchone()
    conn.close()

    content = row[0] if row and row[0] else "준비 중입니다."

    return templates.TemplateResponse("people.html", {
        "request": request,
        "content": content
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    hashed_password = hash_password(password)
    cursor.execute("SELECT id, username, role FROM users WHERE username=? AND password=?",
                   (username, hashed_password))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "아이디 또는 비밀번호가 올바르지 않습니다."
        })

    # Create session
    session_token = secrets.token_urlsafe(32)
    sessions[session_token] = {
        "id": user[0],
        "username": user[1],
        "role": user[2]
    }

    response = RedirectResponse(url="/admin" if user[2] == "admin" else "/", status_code=303)
    response.set_cookie(key="session_token", value=session_token, httponly=True)
    return response

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
    cursor.execute("SELECT * FROM church_about WHERE id=1")
    about_row = cursor.fetchone()
    about = {
        "vision_title": about_row[1] if about_row else "",
        "vision_content": about_row[2] if about_row else "",
        "mission_content": about_row[3] if about_row else ""
    }

    conn.close()

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user,
        "visions": visions,
        "sermons": sermons,
        "shorts": shorts,
        "qtys": qtys,
        "news_list": news_list,
        "church_intro": church_intro,
        "about": about
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

@app.get("/news/{news_id}", response_class=HTMLResponse)
async def view_news(request: Request, news_id: int):
    """View single news post"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Increment views
    cursor.execute("UPDATE news SET views = views + 1 WHERE id=?", (news_id,))
    conn.commit()

    # Get news
    cursor.execute("SELECT * FROM news WHERE id=?", (news_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    news = {"id": row[0], "title": row[1], "content": row[2], "date": row[3], "views": row[4], "author": row[5], "image_path": row[6]}
    conn.close()

    user = get_current_user(request)

    return templates.TemplateResponse("news_detail.html", {
        "request": request,
        "news": news,
        "user": user
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
