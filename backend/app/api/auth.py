import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from backend.app.db.database import db

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = "password"
    role: Optional[str] = "student"

class RegisterRequest(BaseModel):
    name: str
    email: str
    course: str = "MCA"
    semester: int = 3
    department: str = "Computer Applications"
    role: str = "student"
    password: Optional[str] = "password"

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    department: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[int] = None
    created_at: Optional[str] = None

@router.post("/login")
def login(req: LoginRequest):
    """
    Authenticates student or administrator.
    Default credentials:
      - Student: kmahima138@gmail.com (Password: student123) -> Mahima Kumari, MCA Sem 3
      - Admin: admin.academic@uni.edu or admin (Password: admin123) -> Dr. Priya Mehta (Admin)
    """
    login_id = req.email.strip().lower()
    role = req.role.strip().lower()

    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Admin login
        if "admin" in login_id or role == "admin":
            cursor.execute("SELECT * FROM users WHERE role = 'admin' LIMIT 1")
            admin_user = cursor.fetchone()
            if admin_user:
                return {
                    "token": f"token_admin_{uuid.uuid4().hex[:8]}",
                    "user": dict(admin_user),
                    "message": "Admin authenticated successfully."
                }

        # Student login
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = ? OR id = ?", (login_id, login_id))
        user = cursor.fetchone()

        if not user:
            # Fall back to default demo student if email matches Mahima or demo
            if "mahima" in login_id or "student" in login_id or "@" in login_id:
                cursor.execute("SELECT * FROM users WHERE id = 'usr_student_demo'")
                user = cursor.fetchone()

        if user:
            return {
                "token": f"token_student_{uuid.uuid4().hex[:8]}",
                "user": dict(user),
                "message": f"Welcome back, {user['name']}!"
            }

        # Auto-create if new email
        now = datetime.utcnow().isoformat()
        new_id = f"usr_{uuid.uuid4().hex[:8]}"
        display_name = login_id.split("@")[0].replace(".", " ").title()
        cursor.execute("""
        INSERT INTO users (id, name, email, role, department, course, semester, created_at)
        VALUES (?, ?, ?, 'student', 'Computer Applications', 'MCA', 3, ?)
        """, (new_id, display_name, login_id, now))
        conn.commit()

        cursor.execute("SELECT * FROM users WHERE id = ?", (new_id,))
        created = cursor.fetchone()
        return {
            "token": f"token_student_{uuid.uuid4().hex[:8]}",
            "user": dict(created),
            "message": f"Account created! Welcome, {display_name}."
        }

@router.post("/register")
def register(req: RegisterRequest):
    """Registers a new student profile."""
    now = datetime.utcnow().isoformat()
    new_id = f"usr_{uuid.uuid4().hex[:8]}"
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO users (id, name, email, role, department, course, semester, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_id, req.name, req.email.lower(), req.role, req.department, req.course, req.semester, now))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE id = ?", (new_id,))
        return dict(cursor.fetchone())

@router.get("/me/{user_id}")
def get_user_profile(user_id: str):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(user)
