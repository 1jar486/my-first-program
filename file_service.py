import os  # 操作系统接口模块：负责处理文件夹创建、路径拼接、检查文件是否存在
import shutil  # 文件工具模块：负责文件的物理搬运（移动/复制/删除）
import sqlite3  # 数据库模块：负责把你的操作记录永久存进硬盘里的 .db 文件
from datetime import datetime  # 时间模块：负责记录“什么时候”搬的文件

# 定义一个名为 FileOrganizer 的类，就像给“自动搬家机器人”画一张设计图
class FileOrganizer:
    
    # 机器人出厂（初始化）时要做的事情
    def __init__(self):
        # 1. 确定账本的名字
        db_name = "file_history.db"
        self.db_name = db_name
        
        # 2. 定义哪些类型的文件需要搬家（白名单）
        # 注意：ZIP 前面没加点，是因为后面处理后缀时是 .ZIP，这行建议统一加点：'.ZIP'
        self.white_list = ['.JPG', '.PNG', '.DOCX', '.MD', '.MP4', '.ZIP'] 
        
        # 3. 机器人启动时，先看看数据库账本建好了没
        self._init_db() 

    # 内部工具：建立数据库表（如果还没建的话）
    def _init_db(self):
        # 连接到数据库文件（如果文件不存在，会自动创建一个）
        conn = sqlite3.connect(self.db_name) 
        # 创建一个游标，相当于数据库里的“钢笔”，用来写指令
        cursor = conn.cursor()
        
        # 使用 SQL 语句：如果 move_logs 这张表不存在，就创建它
        # 包含：ID(自动编号), 文件名, 原始路径, 目标路径, 时间
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS move_logs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT,
                source_path TEXT,
                dest_path TEXT,
                move_time TEXT   
            )
        ''')
        # 提交操作，相当于按下了“保存”键
        conn.commit()
        # 关闭连接，释放资源
        conn.close()

    # 内部工具：往账本里记一笔搬家记录
    def log_move(self, file_name, source_path, dest_path, move_time):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # 使用 ? 作为占位符，安全地把数据填进 SQL 语句中
        cursor.execute('INSERT INTO move_logs (file_name, source_path, dest_path, move_time) VALUES (?, ?, ?, ?)', 
               (file_name, source_path, dest_path, move_time))
        
        conn.commit() # 重点：不 commit，数据就不会存进硬盘
        conn.close()

    # 机器人的核心功能：开始整理
    def start_organize(self, target_path):
        # 获取当前运行的这个 Python 脚本的名字，避免把自己也给搬走了
        current_script = os.path.basename(__file__)
        
        # 遍历目标文件夹里的每一个项目（文件或文件夹）
        for file in os.listdir(target_path):
            # 拼接出这个项目的完整路径（例如：C:/Users/Desktop/test.jpg）
            full_path = os.path.join(target_path, file)

            # 如果这个项目不是一个文件（比如它是另一个文件夹），就跳过它
            if not os.path.isfile(full_path):
                continue
            
            # 把文件名和后缀名拆开，例如 "test" 和 ".jpg"
            name, ext = os.path.splitext(file)
            # 统一把后缀变成大写（.jpg -> .JPG），方便跟白名单对比
            ext_upper = ext.upper()

            # 过滤逻辑：
            # 1. 如果是脚本自己，不搬
            # 2. 如果是数据库文件，不搬
            # 3. 如果后缀名不在白名单里，也不搬
            if file == current_script or file == self.db_name or ext_upper not in self.white_list:
                continue
            
            # 确定分类文件夹的名字（比如 .JPG 去掉点，文件夹名就是 JPG）
            folder_name = ext_upper[1:]

            # 拼接出分类文件夹的完整路径
            target_folder = os.path.join(target_path, folder_name)

            # 如果这个分类文件夹还不存在，就现场新建一个
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            # 确定文件搬家后的最终目标路径
            target_file_path = os.path.join(target_folder, file)

            # 防止重名：如果目标地已经有一个同名文件了
            count = 1
            while os.path.exists(target_file_path):
                # 给文件名加个数字后缀，比如 test_1_.jpg
                new_name = f"{name}_{count}_{ext}"
                target_file_path = os.path.join(target_folder, new_name)
                count += 1
            
            # 尝试执行搬家和记录
            try:
                # 1. 物理搬运：从 full_path 移到 target_file_path
                shutil.move(full_path, target_file_path)
                
                # 2. 调用记账功能：传入文件名、旧地址、新地址、当前时间
                self.log_move(file, full_path, target_file_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                # 3. 在屏幕上告诉用户成功了
                print(f"已整理：{file} -> {folder_name}") 
            except Exception as e:
                # 如果中间出错了（比如文件被占用），打印出错误原因
                print(f"移动 {file} 失败，原因：{e}")

        print(f"整理完成")

# 程序的启动入口
if __name__ == "__main__":
    # 1. 实例化：让“设计图”变成一个真正的“机器人”
    organizer = FileOrganizer()
    
    # 2. 设定要整理哪里的文件（这里用的桌面测试目录）
    test_dir = r"C:\Users\Administrator\Desktop\自动整理测试"
    
    # 3. 环境准备：如果目录不存在就建一个
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        # 顺手写一个空白的 jpg 文件进去，保证程序运行能看到效果
        with open(os.path.join(test_dir, "test.jpg"), "w") as f:
            f.write("test")

    # 4. 下达指令：让机器人开始干活
    organizer.start_organize(test_dir)