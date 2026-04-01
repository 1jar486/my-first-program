# -*- coding: utf-8 -*-
import sqlite3
import datetime

class DatabaseManager:
    def __init__(self, db_name="super_study.db"):
        self.db_name = db_name
        self.init_db()

    def _execute(self, sql, params=()):
        """内部执行引擎"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            if sql.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            conn.commit()
            return cursor.lastrowid

    def init_db(self):
        """初始化表结构"""
        tables = [
            '''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, create_date TEXT, is_completed INTEGER DEFAULT 0)''',
            '''CREATE TABLE IF NOT EXISTS pomodoro_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER, focus_date TEXT, focus_minutes INTEGER)''',
            '''CREATE TABLE IF NOT EXISTS review_plan (id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER, next_review_date TEXT, review_stage INTEGER DEFAULT 0)''',
            '''CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, create_date TEXT, update_date TEXT)'''
        ]
        for sql in tables:
            self._execute(sql)

    # --- 笔记模块数据接口 ---
    def get_notes(self, keyword=""):
        if keyword:
            return self._execute("SELECT id, title FROM notes WHERE title LIKE ? ORDER BY update_date DESC", (f"%{keyword}%",))
        return self._execute("SELECT id, title FROM notes ORDER BY update_date DESC")

    def get_note(self, note_id):
        res = self._execute("SELECT title, content, create_date, update_date FROM notes WHERE id=?", (note_id,))
        return res[0] if res else None

    def save_note(self, note_id, title, content):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if note_id:
            self._execute("UPDATE notes SET title=?, content=?, update_date=? WHERE id=?", (title, content, now, note_id))
        else:
            self._execute("INSERT INTO notes (title, content, create_date, update_date) VALUES (?, ?, ?, ?)", (title, content, now, now))

    def delete_note(self, note_id):
        self._execute("DELETE FROM notes WHERE id=?", (note_id,))

    # --- 番茄钟与热力图模块数据接口 ---
    def log_pomodoro(self, minutes, task_id=0):
        """记录专注时间，这是热力图的数据源"""
        today = datetime.date.today().strftime("%Y-%m-%d")
        self._execute("INSERT INTO pomodoro_logs (task_id, focus_date, focus_minutes) VALUES (?, ?, ?)", (task_id, today, minutes))

    def get_heatmap_stats(self, days=30):
        """获取热力图数据字典"""
        data = {}
        for i in range(days):
            date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            res = self._execute("SELECT SUM(focus_minutes) FROM pomodoro_logs WHERE focus_date = ?", (date,))
            data[date] = res[0][0] if res[0][0] else 0
        return dict(sorted(data.items()))

    # --- 智能复习模块数据接口 ---
    def add_review_task(self, title, content):
        now = datetime.date.today().strftime("%Y-%m-%d")
        task_id = self._execute("INSERT INTO tasks (content, create_date) VALUES (?, ?)", (f"{title}\n{content}", now))
        self._execute("INSERT INTO review_plan (task_id, next_review_date, review_stage) VALUES (?, ?, ?)", (task_id, now, 0))

    def get_due_reviews(self):
        return self._execute("""
            SELECT r.id, t.content, r.review_stage, r.next_review_date 
            FROM review_plan r JOIN tasks t ON r.task_id = t.id 
            ORDER BY r.next_review_date ASC
        """)
        
    def update_review_stage(self, plan_id, new_stage, next_date):
        self._execute("UPDATE review_plan SET review_stage=?, next_review_date=? WHERE id=?", (new_stage, next_date, plan_id))
        
    def delete_review(self, plan_id):
        self._execute("DELETE FROM review_plan WHERE id=?", (plan_id,))