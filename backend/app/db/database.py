import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DB_URL.replace("sqlite:///", "")

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        """Initializes tables and seeds default user profiles and categories."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL DEFAULT 'student',
                department TEXT,
                course TEXT,
                semester INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Documents
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                filename TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'general',
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                page_count INTEGER DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending',
                error_message TEXT,
                chunk_count INTEGER DEFAULT 0,
                uploaded_by TEXT DEFAULT 'admin',
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                version INTEGER DEFAULT 1
            )
            """)

            # Document Chunks (for fast metadata & text lookup)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                page_number INTEGER NOT NULL,
                metadata_json TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            )
            """)

            # Conversations
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Messages
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                evidence_level TEXT DEFAULT 'strong',
                citations_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
            )
            """)

            # Notices
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS notices (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                title TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'general',
                summary TEXT NOT NULL,
                affected_dept TEXT,
                affected_semester TEXT,
                action_required TEXT,
                deadline TEXT,
                published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE SET NULL
            )
            """)

            # Academic Events & Deadlines
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS academic_events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                event_date TEXT NOT NULL,
                event_type TEXT NOT NULL DEFAULT 'deadline',
                audience TEXT DEFAULT 'All Students',
                source_document_id TEXT,
                source_page INTEGER,
                FOREIGN KEY (source_document_id) REFERENCES documents (id) ON DELETE SET NULL
            )
            """)

            # Feedback
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                message_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE
            )
            """)

            # Seed default demo users if empty
            cursor.execute("SELECT COUNT(*) as count FROM users")
            if cursor.fetchone()["count"] == 0:
                now = datetime.utcnow().isoformat()
                cursor.execute("""
                INSERT INTO users (id, name, email, role, department, course, semester, created_at)
                VALUES 
                ('usr_student_demo', 'Aarav Sharma', 'aarav.sharma@uni.edu', 'student', 'Computer Science & AI', 'B.Tech', 4, ?),
                ('usr_admin_demo', 'Dr. Priya Mehta (Admin)', 'admin.academic@uni.edu', 'admin', 'Academic Registrar Office', 'Faculty', NULL, ?)
                """, (now, now))

            conn.commit()

db = Database()
