# -*- coding: utf-8 -*-
import sys
import os
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont

# 修复部分打包环境插件缺失问题
try:
    plugin_path = os.path.join(os.path.dirname(__import__('PyQt5').__file__), "Qt5", "plugins", "platforms")
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
except Exception: pass

# 导入自定义重构模块
from styles import MAIN_STYLE, DANGER_BUTTON
from database import DatabaseManager
from file_service import FileOrganizer
from heatmap import VictoryHeatmapWindow

REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]

class SuperStudyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StudyProgramPlus")
        self.resize(1150, 850)
        self.setStyleSheet(MAIN_STYLE)

        # 初始化核心服务 (Model)
        self.db = DatabaseManager()
        self.file_service = FileOrganizer()
        
        # 状态管理 (State)
        self.current_note_id = None
        self.current_review_id = None
        self.time_left = 25 * 60
        self.is_running = False
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.init_ui()
        self.refresh_notes_list()
        self.refresh_review_list()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 25)

        # 顶栏
        header = QWidget()
        header.setObjectName("appHeader")
        header.setFixedHeight(110)
        h_layout = QHBoxLayout(header)
        t_box = QVBoxLayout()
        t_box.addWidget(QLabel("Study+ 智能学习助手", objectName="heroTitle"))
        t_box.addWidget(QLabel("专注力 / 记忆曲线 / 文件自动化 / 知识库", objectName="heroSubtitle"))
        h_layout.addLayout(t_box)
        h_layout.addStretch()
        h_layout.addWidget(QLabel("先启动，再优化", objectName="headerTagPill"))
        main_layout.addWidget(header)

        # 标签页容器
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tab_pomo = QWidget()
        self.tab_review = QWidget()
        self.tab_organizer = QWidget()
        self.tab_notes = QWidget()

        self.tabs.addTab(self.tab_pomo, "🍅 番茄专注")
        self.tabs.addTab(self.tab_review, "🧠 智能复习")
        self.tabs.addTab(self.tab_organizer, "📂 文件管理")
        self.tabs.addTab(self.tab_notes, "📓 学习笔记")
        main_layout.addWidget(self.tabs)

        self.setup_pomo_ui()
        self.setup_review_tab()
        self.setup_organizer_ui()
        self.setup_notes_ui()
  
        # ================= 1. 番茄钟逻辑 =================
    def setup_pomo_ui(self):
        layout = QVBoxLayout(self.tab_pomo)
        layout.setAlignment(Qt.AlignCenter)

        self.lbl_time = QLabel("25:00", objectName="TimerDisplay")
        self.lbl_time.setAlignment(Qt.AlignCenter)

        btn_layout = QHBoxLayout()
        self.btn_start_pomo = QPushButton("开始专注", objectName="btnPrimary")
        self.btn_start_pomo.setFixedSize(200, 60)
        self.btn_start_pomo.clicked.connect(self.toggle_timer)

        btn_reset = QPushButton("重置")
        btn_reset.setFixedSize(120, 60)
        btn_reset.clicked.connect(self.reset_timer)
        
        btn_heatmap = QPushButton("🏆 成就看板")
        btn_heatmap.setFixedSize(120, 60)
        btn_heatmap.setStyleSheet("background-color: #a5d6a7; color: #1b5e20;")
        btn_heatmap.clicked.connect(self.open_heatmap)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_start_pomo)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(btn_reset)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(btn_heatmap)
        btn_layout.addStretch()

        layout.addStretch()
        layout.addWidget(self.lbl_time)
        layout.addLayout(btn_layout)
        layout.addStretch()

    def toggle_timer(self):
        if not self.is_running:
            self.timer.start(1000)
            self.btn_start_pomo.setText("暂停")
            self.btn_start_pomo.setStyleSheet("background-color: #e67e22;") 
        else:
            self.timer.stop()
            self.btn_start_pomo.setText("继续专注")
            self.btn_start_pomo.setStyleSheet("") 
        self.is_running = not self.is_running

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.time_left = 25 * 60
        self.lbl_time.setText("25:00")
        self.btn_start_pomo.setText("开始专注")
        self.btn_start_pomo.setStyleSheet("")

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            mins, secs = divmod(self.time_left, 60)
            self.lbl_time.setText(f"{mins:02d}:{secs:02d}")
        else:
            self.timer.stop()
            self.is_running = False
            self.db.log_pomodoro(25) # 自动同步数据至数据库
            QMessageBox.information(self, "时间到", "太棒了！已完成25分钟专注，数据已同步至热力图。")
            self.reset_timer()

    def open_heatmap(self):
        self.heatmap_win = VictoryHeatmapWindow(self.db)
        self.heatmap_win.show()

    # ================= 2. 智能复习逻辑 =================
    def setup_review_tab(self):
        main_layout = QHBoxLayout(self.tab_review)
        left_panel, right_panel = QVBoxLayout(), QVBoxLayout()
        right_panel.setContentsMargins(10, 0, 10, 0)

        # 左侧列表
        left_btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 刷新列表", objectName="btnPrimary")
        btn_add = QPushButton("+ 添加复习", objectName="btnPrimary")
        btn_refresh.clicked.connect(self.refresh_review_list)
        btn_add.clicked.connect(self.add_review_task)
        left_btn_layout.addWidget(btn_refresh)
        left_btn_layout.addWidget(btn_add)
        
        self.list_review = QListWidget()
        self.list_review.currentItemChanged.connect(self.load_review_content)
        left_panel.addLayout(left_btn_layout)
        left_panel.addWidget(self.list_review)

        # 右侧内容显示
        self.review_display = QTextEdit()
        self.review_display.setReadOnly(True)
        self.review_display.setPlaceholderText("💡 请从左侧列表中选择...")
        
        op_btn_layout = QHBoxLayout()
        btn_mastered = QPushButton("✅ 已掌握")
        btn_forget = QPushButton("❌ 记不清了")
        btn_remove = QPushButton("🗑️ 移出计划")
        btn_remove.setStyleSheet("background-color: #ffab91; border-radius: 15px;")
        
        btn_mastered.clicked.connect(lambda: self.handle_review("mastered"))
        btn_forget.clicked.connect(lambda: self.handle_review("forget"))
        btn_remove.clicked.connect(lambda: self.handle_review("remove"))
        
        op_btn_layout.addWidget(btn_mastered)
        op_btn_layout.addWidget(btn_forget)
        op_btn_layout.addWidget(btn_remove)

        right_panel.addWidget(self.review_display, 7)
        right_panel.addLayout(op_btn_layout, 3)
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)

    def refresh_review_list(self):
        self.list_review.clear()
        for row in self.db.get_due_reviews():
            title = row[1].split('\n')[0][:15] + "..."
            item = QListWidgetItem(f"📅 阶段 {row[2]} | {title}")
            item.setData(Qt.UserRole, {"id": row[0], "content": row[1], "stage": row[2]})
            self.list_review.addItem(item)
            
    def load_review_content(self, current, previous):
        if not current: 
            self.review_display.clear()
            self.current_review_id = None
            return
        data = current.data(Qt.UserRole)
        self.current_review_id = data["id"]
        self.current_review_stage = data["stage"]
        self.review_display.setPlainText(f"📝 任务详情：\n\n{data['content']}\n\n" + "-"*30 + "\n💡 提示：请真实反馈记忆情况。")

    def add_review_task(self):
        title, ok1 = QInputDialog.getText(self, '添加', '复习主题:')
        if ok1 and title:
            content, ok2 = QInputDialog.getMultiLineText(self, '添加', '详细内容:')
            if ok2:
                self.db.add_review_task(title, content)
                self.refresh_review_list()

    def handle_review(self, action):
        if not self.current_review_id: return
        
        if action == "remove":
            self.db.delete_review(self.current_review_id)
        elif action == "mastered":
            next_stage = self.current_review_stage + 1
            if next_stage >= len(REVIEW_INTERVALS):
                self.db.delete_review(self.current_review_id)
                QMessageBox.information(self, "恭喜", "该知识点已完全掌握！")
            else:
                days = REVIEW_INTERVALS[next_stage]
                next_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
                self.db.update_review_stage(self.current_review_id, next_stage, next_date)
        elif action == "forget":
            next_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            self.db.update_review_stage(self.current_review_id, 0, next_date)
            
        self.refresh_review_list()
        self.review_display.clear()
    
        # ================= 3. 文件管理逻辑 =================
    def setup_organizer_ui(self):
        layout = QVBoxLayout(self.tab_organizer)
        layout.setContentsMargins(40, 40, 40, 40)
        
        info = QLabel("📂 自动化文件归档系统")
        info.setStyleSheet("font-size: 24px; font-weight: bold; color: #2d5a4a;")
        layout.addWidget(info)
        layout.addWidget(QLabel("一键将文件夹内杂乱的文件按后缀名自动分类。"))

        path_box = QHBoxLayout()
        self.input_org_path = QLineEdit()
        self.input_org_path.setPlaceholderText("例如: C:/Users/Downloads")
        btn_browse = QPushButton("选择")
        btn_browse.clicked.connect(lambda: self.input_org_path.setText(QFileDialog.getExistingDirectory()))
        path_box.addWidget(self.input_org_path)
        path_box.addWidget(btn_browse)
        layout.addLayout(path_box)

        btn_run = QPushButton("开始一键整理", objectName="btnPrimary")
        btn_run.setFixedHeight(50)
        btn_run.clicked.connect(self.run_organize)
        layout.addWidget(btn_run)

        self.list_org_logs = QListWidget()
        layout.addWidget(QLabel("整理日志："))
        layout.addWidget(self.list_org_logs)

    def run_organize(self):
        path = self.input_org_path.text().strip()
        if not path or not os.path.isdir(path): return QMessageBox.warning(self, "错误", "路径无效")
        self.list_org_logs.clear()
        logs = self.file_service.start_organize(path)
        for log in logs: self.list_org_logs.addItem(log)

    # ================= 4. 学习笔记逻辑 =================
    def setup_notes_ui(self):
        main_layout = QHBoxLayout(self.tab_notes)
        left_panel, right_panel = QVBoxLayout(), QVBoxLayout()
        right_panel.setSpacing(10)

        self.search_notes = QLineEdit()
        self.search_notes.setPlaceholderText("🔍 搜索笔记...")
        self.search_notes.textChanged.connect(self.refresh_notes_list)
        self.list_notes = QListWidget()
        self.list_notes.currentItemChanged.connect(self.load_note)
        btn_new = QPushButton("+ 新建笔记", objectName="btnPrimary")
        btn_new.clicked.connect(self.clear_note_editor)
        left_panel.addWidget(self.search_notes)
        left_panel.addWidget(self.list_notes)
        left_panel.addWidget(btn_new)

        self.input_title = QLineEdit(placeholderText="输入标题...")
        self.lbl_meta = QLabel("创建时间：— | 更新时间：—")
        self.lbl_meta.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        self.editor = QTextEdit(placeholderText="输入正文...")
        
        btn_box = QHBoxLayout()
        self.btn_del = QPushButton("🗑️ 删除笔记")
        self.btn_del.setStyleSheet(DANGER_BUTTON)
        self.btn_del.hide()
        self.btn_del.clicked.connect(self.delete_note)
        
        btn_save = QPushButton("💾 保存笔记", objectName="btnPrimary")
        btn_save.clicked.connect(self.save_note)
        
        btn_box.addWidget(self.btn_del)
        btn_box.addWidget(btn_save)

        right_panel.addWidget(self.input_title)
        right_panel.addWidget(self.lbl_meta)
        right_panel.addWidget(self.editor)
        right_panel.addLayout(btn_box)

        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 3)

    def refresh_notes_list(self):
        self.list_notes.clear()
        for row in self.db.get_notes(self.search_notes.text().strip()):
            item = QListWidgetItem(row[1])
            item.setData(Qt.UserRole, row[0])
            self.list_notes.addItem(item)

    def load_note(self, current, previous):
        if not current: return self.clear_note_editor()
        self.current_note_id = current.data(Qt.UserRole)
        note = self.db.get_note(self.current_note_id)
        if note:
            self.input_title.setText(note[0]); self.editor.setPlainText(note[1])
            self.lbl_meta.setText(f"创建：{note[2][:10]} | 更新：{note[3][:10]}")
            self.btn_del.show()

    def clear_note_editor(self):
        self.current_note_id = None; self.input_title.clear(); self.editor.clear()
        self.lbl_meta.setText("创建时间：— | 更新时间：—"); self.btn_del.hide()

    def save_note(self):
        title = self.input_title.text().strip() or "未命名笔记"
        self.db.save_note(self.current_note_id, title, self.editor.toPlainText())
        self.refresh_notes_list(); QMessageBox.information(self, "成功", "已保存！")

    def delete_note(self):
        if not self.current_note_id: return
        if QMessageBox.question(self, '确认', "确定删除？") == QMessageBox.Yes:
            self.db.delete_note(self.current_note_id)
            self.refresh_notes_list(); 
            self.clear_note_editor()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 设置应用级全局字体，增强 UI 质感
    app.setFont(QFont("Microsoft YaHei UI", 10))
    
    window = SuperStudyApp()
    window.show()
    sys.exit(app.exec_())

    
