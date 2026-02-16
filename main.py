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

DB_PATH = "church.db"
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

    # Check if admin exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    if cursor.fetchone()[0] == 0:
        # Create default admin (username: admin, password: admin123)
        cursor.execute("""
            INSERT INTO users (username, password, role, created_at)
            VALUES (?, ?, 'admin', ?)
        """, ('admin', hash_password('admin123'), datetime.now().isoformat()))

    # Check if church info exists
    cursor.execute("SELECT COUNT(*) FROM church_info")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO church_info (id, content, updated_at)
            VALUES (1, '더하는 교회는 하나님의 사랑과 예수 그리스도의 복음을 전하는 믿음의 공동체입니다.', ?)
        """, (datetime.now().isoformat(),))

    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM sermons")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO sermons (title, pastor, date, description)
            VALUES
            ('하나님의 사랑', '김한기 목사', '2026-02-16', '요한복음 3:16을 중심으로 하나님의 무한한 사랑에 대해 나눕니다.'),
            ('믿음의 여정', '김한기 목사', '2026-02-09', '히브리서 11장을 통해 믿음의 선진들의 삶을 배웁니다.'),
            ('평안의 근원', '김한기 목사', '2026-02-02', '빌립보서 4:6-7을 통해 진정한 평안을 찾는 법을 나눕니다.')
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
            ('2026년 교회 비전', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', '2026-01-15', '관리자')
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
        "news_list": news_list,
        "church_intro": church_intro,
        "user": user
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

    # Get all news
    cursor.execute("SELECT * FROM news ORDER BY date DESC")
    news_list = [{"id": row[0], "title": row[1], "content": row[2], "date": row[3], "views": row[4], "author": row[5], "image_path": row[6]}
                for row in cursor.fetchall()]

    # Get church info
    cursor.execute("SELECT content FROM church_info WHERE id=1")
    result = cursor.fetchone()
    church_intro = result[0] if result else ""

    conn.close()

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user,
        "visions": visions,
        "sermons": sermons,
        "shorts": shorts,
        "news_list": news_list,
        "church_intro": church_intro
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
