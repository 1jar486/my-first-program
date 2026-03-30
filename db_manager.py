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
            focus_date TEXT,     -- 专注日期 (例如 2024-05-20)
            focus_minutes INTEGER -- 专注了多少分钟
        )
    ''')

    # 3. 艾宾浩斯复习追踪表
    run_sql('''
        CREATE TABLE IF NOT EXISTS review_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            next_review_date TEXT, -- 下一次复习的具体日期
            review_stage INTEGER DEFAULT 1, -- 当前处于第几个复习阶段 (1, 2, 4, 7, 15天...)
            mastery_level TEXT     -- 掌握程度 (记得/模糊/忘记)
        )
    ''')
    print("✅ 超级大脑数据库 (super_study.db) 引擎启动成功！三张表已建立。")


if __name__ == "__main__":
    init_db()