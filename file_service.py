import os
import shutil
import sqlite3
from datetime import datetime

class FileOrganizer:
    def __init__(self):
        self.db_name = "file_history.db"
        self.white_list = ['.JPG', '.PNG', '.DOCX', '.MD', '.MP4', '.ZIP'] 
        self._init_db() 

    def _init_db(self):
        conn = sqlite3.connect(self.db_name) 
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS move_logs(
                id INTEGER PRIMARY KEY AUTOINCREMENT, file_name TEXT, source_path TEXT, dest_path TEXT, move_time TEXT)''')
        conn.commit()
        conn.close()

    def log_move(self, file_name, source_path, dest_path, move_time):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO move_logs (file_name, source_path, dest_path, move_time) VALUES (?, ?, ?, ?)', 
               (file_name, source_path, dest_path, move_time))
        conn.commit() 
        conn.close()

    def start_organize(self, target_path):
        current_script = os.path.basename(__file__)
        logs = [] # 核心修复：创建一个列表用于收集结果，传回给主界面

        for file in os.listdir(target_path):
            full_path = os.path.join(target_path, file)
            if not os.path.isfile(full_path): continue
            
            name, ext = os.path.splitext(file)
            ext_upper = ext.upper()

            if file == current_script or file == self.db_name or ext_upper not in self.white_list:
                continue
            
            folder_name = ext_upper[1:]
            target_folder = os.path.join(target_path, folder_name)
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            target_file_path = os.path.join(target_folder, file)
            count = 1
            while os.path.exists(target_file_path):
                new_name = f"{name}_{count}_{ext}"
                target_file_path = os.path.join(target_folder, new_name)
                count += 1
            
            try:
                shutil.move(full_path, target_file_path)
                self.log_move(file, full_path, target_file_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                logs.append(f"✅ 已整理：{file} -> {folder_name}") # 记录成功
            except Exception as e:
                logs.append(f"❌ 移动 {file} 失败，原因：{e}") # 记录失败
                
        # 如果没有移动任何文件，给出友好提示
        if not logs:
            logs.append("ℹ️ 目标文件夹中没有需要整理的白名单文件。")
            
        return logs # 必须返回给 main.py
import os
import shutil
import sqlite3
from datetime import datetime

class FileOrganizer:
    def __init__(self):
        self.db_name = "file_history.db"
        self.white_list = ['.JPG', '.PNG', '.DOCX', '.MD', '.MP4', '.ZIP'] 
        self._init_db() 

    def _init_db(self):
        conn = sqlite3.connect(self.db_name) 
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS move_logs(
                id INTEGER PRIMARY KEY AUTOINCREMENT, file_name TEXT, source_path TEXT, dest_path TEXT, move_time TEXT)''')
        conn.commit()
        conn.close()

    def log_move(self, file_name, source_path, dest_path, move_time):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO move_logs (file_name, source_path, dest_path, move_time) VALUES (?, ?, ?, ?)', 
               (file_name, source_path, dest_path, move_time))
        conn.commit() 
        conn.close()

    def start_organize(self, target_path):
        current_script = os.path.basename(__file__)
        logs = [] # 核心修复：创建一个列表用于收集结果，传回给主界面

        for file in os.listdir(target_path):
            full_path = os.path.join(target_path, file)
            if not os.path.isfile(full_path): continue
            
            name, ext = os.path.splitext(file)
            ext_upper = ext.upper()

            if file == current_script or file == self.db_name or ext_upper not in self.white_list:
                continue
            
            folder_name = ext_upper[1:]
            target_folder = os.path.join(target_path, folder_name)
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            target_file_path = os.path.join(target_folder, file)
            count = 1
            while os.path.exists(target_file_path):
                new_name = f"{name}_{count}_{ext}"
                target_file_path = os.path.join(target_folder, new_name)
                count += 1
            
            try:
                shutil.move(full_path, target_file_path)
                self.log_move(file, full_path, target_file_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                logs.append(f"✅ 已整理：{file} -> {folder_name}") # 记录成功
            except Exception as e:
                logs.append(f"❌ 移动 {file} 失败，原因：{e}") # 记录失败
                
        # 如果没有移动任何文件，给出友好提示
        if not logs:
            logs.append("ℹ️ 目标文件夹中没有需要整理的白名单文件。")
            
        return logs # 必须返回给 main.py