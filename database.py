import sqlite3
import datetime

def run_sql(sql, params=()):
    """数据库通用引擎"""
    conn = sqlite3.connect("super_study.db")
    cursor = conn.cursor()
    cursor.execute(sql, params)

    if sql.strip().upper().startswith("SELECT"):
        data = cursor.fetchall()
    else:
        conn.commit()
        # 核心修复：返回最后插入的 ID，方便添加复习任务时做关联
        data = cursor.lastrowid 

    conn.close()
    return data

def init_db():
    """初始化全新的高阶数据库"""
    run_sql('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, create_date TEXT, is_completed INTEGER DEFAULT 0)''')
    run_sql('''CREATE TABLE IF NOT EXISTS pomodoro_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER, focus_date TEXT, focus_minutes INTEGER)''')
    run_sql('''CREATE TABLE IF NOT EXISTS review_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER, next_review_date TEXT, review_stage INTEGER DEFAULT 1, mastery_level TEXT)''')
    run_sql('''CREATE TABLE IF NOT EXISTS notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, create_date TEXT, update_date TEXT)''')
    print("✅ 超级大脑数据库 (super_study.db) 引擎启动成功！")

# --- 笔记接口 ---
def get_notes_list(keyword=""):
    if keyword:
        return run_sql("SELECT id, title FROM notes WHERE title LIKE ? ORDER BY update_date DESC", (f"%{keyword}%",))
    return run_sql("SELECT id, title FROM notes ORDER BY update_date DESC")

def get_note_by_id(note_id):
    res = run_sql("SELECT title, content, create_date, update_date FROM notes WHERE id=?", (note_id,))
    return res[0] if res else None

def save_or_update_note(note_id, title, content):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if note_id:
        run_sql("UPDATE notes SET title=?, content=?, update_date=? WHERE id=?", (title, content, now, note_id))
        return False 
    else:
        run_sql("INSERT INTO notes (title, content, create_date, update_date) VALUES (?, ?, ?, ?)", (title, content, now, now))
        return True 

# --- 修复后的删除与复习接口 ---
def delete_note_by_id(note_id):
    """修复：去除了错误的 self 参数，统一使用 run_sql"""
    run_sql("DELETE FROM notes WHERE id = ?", (note_id,))

def add_review_task(title, content):
    """修复：正确分离 task 和 review_plan 的两步插入逻辑"""
    now_date = datetime.date.today().strftime('%Y-%m-%d')
    # 1. 先把任务内容存入 tasks 表，获取到 task_id
    task_id = run_sql("INSERT INTO tasks (content, create_date) VALUES (?, ?)", (f"{title}\n{content}", now_date))
    # 2. 将 task_id 关联到艾宾浩斯复习计划表，初始阶段为 0
    run_sql("INSERT INTO review_plan (task_id, next_review_date, review_stage) VALUES (?, ?, 0)", (task_id, now_date))

if __name__ == "__main__":
    init_db()
import sqlite3
import datetime

def run_sql(sql, params=()):
    """数据库通用引擎"""
    conn = sqlite3.connect("super_study.db")
    cursor = conn.cursor()
    cursor.execute(sql, params)

    if sql.strip().upper().startswith("SELECT"):
        data = cursor.fetchall()
    else:
        conn.commit()
        # 核心修复：返回最后插入的 ID，方便添加复习任务时做关联
        data = cursor.lastrowid 

    conn.close()
    return data

def init_db():
    """初始化全新的高阶数据库"""
    run_sql('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, create_date TEXT, is_completed INTEGER DEFAULT 0)''')
    run_sql('''CREATE TABLE IF NOT EXISTS pomodoro_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER, focus_date TEXT, focus_minutes INTEGER)''')
    run_sql('''CREATE TABLE IF NOT EXISTS review_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER, next_review_date TEXT, review_stage INTEGER DEFAULT 1, mastery_level TEXT)''')
    run_sql('''CREATE TABLE IF NOT EXISTS notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, create_date TEXT, update_date TEXT)''')
    print("✅ 超级大脑数据库 (super_study.db) 引擎启动成功！")

# --- 笔记接口 ---
def get_notes_list(keyword=""):
    if keyword:
        return run_sql("SELECT id, title FROM notes WHERE title LIKE ? ORDER BY update_date DESC", (f"%{keyword}%",))
    return run_sql("SELECT id, title FROM notes ORDER BY update_date DESC")

def get_note_by_id(note_id):
    res = run_sql("SELECT title, content, create_date, update_date FROM notes WHERE id=?", (note_id,))
    return res[0] if res else None

def save_or_update_note(note_id, title, content):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if note_id:
        run_sql("UPDATE notes SET title=?, content=?, update_date=? WHERE id=?", (title, content, now, note_id))
        return False 
    else:
        run_sql("INSERT INTO notes (title, content, create_date, update_date) VALUES (?, ?, ?, ?)", (title, content, now, now))
        return True 

# --- 修复后的删除与复习接口 ---
def delete_note_by_id(note_id):
    """修复：去除了错误的 self 参数，统一使用 run_sql"""
    run_sql("DELETE FROM notes WHERE id = ?", (note_id,))

def add_review_task(title, content):
    """修复：正确分离 task 和 review_plan 的两步插入逻辑"""
    now_date = datetime.date.today().strftime('%Y-%m-%d')
    # 1. 先把任务内容存入 tasks 表，获取到 task_id
    task_id = run_sql("INSERT INTO tasks (content, create_date) VALUES (?, ?)", (f"{title}\n{content}", now_date))
    # 2. 将 task_id 关联到艾宾浩斯复习计划表，初始阶段为 0
    run_sql("INSERT INTO review_plan (task_id, next_review_date, review_stage) VALUES (?, ?, 0)", (task_id, now_date))

if __name__ == "__main__":
    init_db()