import sqlite3
import os
from datetime import datetime, timedelta

DB_NAME = "contextflow.db"
IMAGES_DIR = "clips_images"

def init_db():
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT UNIQUE,
            category TEXT,
            created_at TEXT,
            is_favorite INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def save_clip(content, category):
    if not content or category == "empty":
        return
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Вставляем новый клип
        cursor.execute('''
            INSERT OR IGNORE INTO clips (content, category, created_at, is_favorite)
            VALUES (?, ?, ?, 0)
        ''', (content, category, timestamp))
        
        # 1. Автоматическая очистка элементов старше 7 дней (если они не в избранном)
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("DELETE FROM clips WHERE is_favorite = 0 AND created_at < ?", (week_ago,))
        
        # 2. Лимит истории: оставляем только последние 100 записей (не считая избранное)
        cursor.execute('''
            DELETE FROM clips 
            WHERE is_favorite = 0 AND id NOT IN (
                SELECT id FROM clips WHERE is_favorite = 0 ORDER BY id DESC LIMIT 100
            )
        ''')
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"db error: {e}")

def get_clips(limit=100):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, content, created_at, is_favorite FROM clips ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_favorites():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, content, created_at, is_favorite FROM clips WHERE is_favorite = 1 ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def toggle_favorite_db(clip_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT is_favorite FROM clips WHERE id = ?", (clip_id,))
    row = cursor.fetchone()
    if row:
        new_val = 0 if row[0] == 1 else 1
        cursor.execute("UPDATE clips SET is_favorite = ? WHERE id = ?", (new_val, clip_id))
        conn.commit()
    conn.close()

def delete_clip_db(clip_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
    conn.commit()
    conn.close()

def clear_history_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clips WHERE is_favorite = 0")
    conn.commit()
    conn.close()