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
        data = None

    conn.close()
    return data


def init_db():
    """初始化全新的高阶数据库"""
    # 1. 核心任务表
    run_sql('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            create_date TEXT,
            is_completed INTEGER DEFAULT 0
        )
    ''')

    # 2. 番茄钟时间日志表（为你后续的数据可视化打基础）
    run_sql('''
        CREATE TABLE IF NOT EXISTS pomodoro_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            focus_date TEXT,     
            focus_minutes INTEGER 
        )
    ''')

    # 3. 艾宾浩斯复习追踪表
    run_sql('''
        CREATE TABLE IF NOT EXISTS review_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            next_review_date TEXT, 
            review_stage INTEGER DEFAULT 1, 
            mastery_level TEXT     
        )
    ''')

    # 新增表
    # 4.学习笔记表
    run_sql('''
        CREATE TABLE IF NOT EXISTS notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, 
            content TEXT, 
            create_date TEXT, 
            update_date TEXT 
        )
    ''')

    print("✅ 超级大脑数据库 (super_study.db) 引擎启动成功！四张表已建立。")
# --- 以下是新增的笔记功能接口 ---

def get_notes_list(keyword=""):
    """获取笔记列表，支持关键词搜索"""
    if keyword:
        return run_sql("SELECT id, title FROM notes WHERE title LIKE ? ORDER BY update_date DESC", (f"%{keyword}%",))
    return run_sql("SELECT id, title FROM notes ORDER BY update_date DESC")

def get_note_by_id(note_id):
    """根据 ID 获取单篇笔记的详细内容"""
    res = run_sql("SELECT title, content, create_date, update_date FROM notes WHERE id=?", (note_id,))
    return res[0] if res else None

def save_or_update_note(note_id, title, content):
    """保存笔记：如果 ID 存在则更新，不存在则插入新记录"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if note_id:
        # 更新现有笔记
        run_sql("UPDATE notes SET title=?, content=?, update_date=? WHERE id=?",
                (title, content, now, note_id))
        return False # 返回 False 表示执行的是更新
    else:
        # 插入新笔记
        run_sql("INSERT INTO notes (title, content, create_date, update_date) VALUES (?, ?, ?, ?)",
                (title, content, now, now))
        return True # 返回 True 表示执行的是新建

# --- 在 2_db_manager.py 中添加 ---

def delete_note_by_id(self, note_id):
    """根据 ID 删除笔记"""
    query = "DELETE FROM notes WHERE id = ?"
    return self.execute_query(query, (note_id,))

def add_review_task(self, title, content):
    """手动添加复习任务"""
    import datetime
    # 初始状态设为 0 (新任务), 下次复习时间设为今天
    next_review = datetime.date.today().strftime('%Y-%m-%d')
    query = "INSERT INTO review_tasks (title, content, stage, next_review) VALUES (?, ?, 0, ?)"
    return self.execute_query(query, (title, content, next_review))

if __name__ == "__main__":
    init_db()