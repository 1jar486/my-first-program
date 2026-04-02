# -*- coding: utf-8 -*-
import sys
import os
import datetime
import random
import shutil
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QPixmap, QIcon

# 修复重复的 import，只保留一次整洁的调用
from database import (
    run_sql, init_db, get_notes_list,
    get_note_by_id, save_or_update_note,
    delete_note_by_id, add_review_task
)
from styles import (
    QSS_APP_GLOBAL, QSS_REVIEW_CARD,
    QSS_REVIEW_CARD_SELECTED, build_tab_bar_qss, DANGER_BUTTON
)

try:
    plugin_path = os.path.join(os.path.dirname(__import__('PyQt5').__file__), "Qt5", "plugins", "platforms")
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
except Exception:
    pass

try:
    from file_service import FileOrganizer
except ImportError:
    class FileOrganizer:
        def __init__(self): self.white_list = ['.JPG', '.PNG', '.PDF', '.DOCX']
        def start_organize(self, path): return ["⚠️ 未找到 file_service.py"]

REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]

def fmt_cn_date(ymd: str) -> str:
    if not ymd or len(ymd) < 10: return "—"
    try:
        y, m, d = int(ymd[0:4]), int(ymd[5:7]), int(ymd[8:10])
        return f"{y}年{m}月{d}日"
    except (ValueError, IndexError):
        return ymd

class SuperStudyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StudyProgramPlus")
        self.resize(1150, 850)
        self.setStyleSheet(QSS_APP_GLOBAL)

        self.file_service = FileOrganizer()
        self.current_note_id = None
        
        # 替换原有混乱的复习变量，统一使用 ID 追踪
        self.current_review_id = None 

        self.time_left = 25 * 60
        self.is_running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.init_ui()
        # 启动时自动加载列表
        self.refresh_notes_list()
        self.refresh_review_list()

    def _build_header(self):
        header = QWidget()
        header.setObjectName("appHeader")
        header.setFixedHeight(110)
        layout = QHBoxLayout(header)

        title_box = QVBoxLayout()
        m_title = QLabel("Study+ 智能学习助手")
        m_title.setObjectName("heroTitle")
        s_title = QLabel("专注力 / 记忆曲线 / 文件自动化 / 知识库")
        s_title.setObjectName("heroSubtitle")
        title_box.addWidget(m_title); title_box.addWidget(s_title)

        layout.addLayout(title_box); layout.addStretch()
        self.lbl_encouragement = QLabel("先启动，再优化")
        self.lbl_encouragement.setObjectName("headerTagPill")
        layout.addWidget(self.lbl_encouragement)
        return header

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 25)
        main_layout.addWidget(self._build_header())

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.tab_pomo = QWidget()
        self.tab_review = QWidget()
        self.tab_organizer = QWidget()
        self.tab_notes = QWidget()

        self.tabs.addTab(self.tab_pomo, "番茄专注")
        self.tabs.addTab(self.tab_review, "智能复习")
        self.tabs.addTab(self.tab_organizer, "文件管理")
        self.tabs.addTab(self.tab_notes, "学习笔记")
        main_layout.addWidget(self.tabs)

        self.setup_pomo_ui()
        self.setup_review_tab()
        self.setup_organizer_ui()
        self.setup_notes_ui()

    # --- 模块 1: 番茄钟 ---
    def setup_pomo_ui(self):
        layout = QVBoxLayout(self.tab_pomo)
        layout.setAlignment(Qt.AlignCenter)

        self.lbl_time = QLabel("25:00")
        self.lbl_time.setObjectName("TimerDisplay")
        self.lbl_time.setAlignment(Qt.AlignCenter)
        self.lbl_time.setStyleSheet("font-size: 120px; font-weight: bold; color: #2d5a4a; margin: 20px;")

        btn_layout = QHBoxLayout()
        self.btn_start_pomo = QPushButton("开始专注")
        self.btn_start_pomo.setFixedSize(200, 60)
        self.btn_start_pomo.setObjectName("btnPrimary")
        self.btn_start_pomo.clicked.connect(self.toggle_timer)

        btn_reset = QPushButton("重置")
        btn_reset.setFixedSize(120, 60)
        btn_reset.clicked.connect(self.reset_timer)

        btn_layout.addStretch(); btn_layout.addWidget(self.btn_start_pomo)
        btn_layout.addSpacing(20); btn_layout.addWidget(btn_reset); btn_layout.addStretch()

        layout.addStretch(); layout.addWidget(self.lbl_time)
        layout.addLayout(btn_layout); layout.addStretch()    

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
            # 逻辑修复：将成功的番茄钟记录正式写入数据库，为后续热力图提供数据支持
            now_date = datetime.date.today().strftime('%Y-%m-%d')
            run_sql("INSERT INTO pomodoro_logs (focus_date, focus_minutes) VALUES (?, ?)", (now_date, 25))
            QMessageBox.information(self, "时间到", "太棒了！已记录 25 分钟专注时间。")
            self.reset_timer()

    # --- 模块 2: 智能复习 ---
    def setup_review_tab(self):
        main_layout = QHBoxLayout(self.tab_review)

        left_panel = QVBoxLayout()
        left_btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("🔄 刷新列表")
        self.btn_add_review = QPushButton("+ 添加复习")

        left_btn_layout.addWidget(self.btn_refresh)
        left_btn_layout.addWidget(self.btn_add_review)

        self.list_review = QListWidget()
        self.list_review.currentItemChanged.connect(self.load_review_content)

        left_panel.addLayout(left_btn_layout)
        left_panel.addWidget(self.list_review)

        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(10, 0, 10, 0)

        self.review_content_display = QTextEdit()
        self.review_content_display.setReadOnly(True)
        self.review_content_display.setPlaceholderText("💡 请从左侧列表中选择一个复习任务...")
        self.review_content_display.setStyleSheet("background-color: #ffffff; border: 1px solid #d4e4da; border-radius: 15px; padding: 10px;")

        op_btn_layout = QHBoxLayout()
        op_btn_layout.setSpacing(10)  

        self.btn_mastered = QPushButton("✅ 这一阶段已掌握")
        self.btn_forget = QPushButton("❌ 记不清了，重来")
        self.btn_remove_task = QPushButton("🗑️ 移出复习计划")
        self.btn_remove_task.setStyleSheet("background-color: #ffab91; color: white; border-radius: 15px;")

        op_btn_layout.addWidget(self.btn_mastered)
        op_btn_layout.addWidget(self.btn_forget)
        op_btn_layout.addWidget(self.btn_remove_task)

        right_panel.addWidget(self.review_content_display, 7)
        right_panel.addLayout(op_btn_layout, 3)

        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)

        self.btn_refresh.clicked.connect(self.refresh_review_list)
        self.btn_add_review.clicked.connect(self.show_add_review_dialog)
        self.btn_mastered.clicked.connect(self.handle_review_mastered)
        self.btn_forget.clicked.connect(self.handle_review_forget)
        self.btn_remove_task.clicked.connect(self.handle_remove_review_task)

    def load_review_content(self, current, previous):
        if not current:
            self.review_content_display.clear()
            self.current_review_id = None
            return
        try:
            # 逻辑修复：通过之前绑定的 ID，去数据库查询真正的完整内容
            self.current_review_id = current.data(Qt.UserRole)
            res = run_sql("SELECT t.content FROM review_plan r JOIN tasks t ON r.task_id = t.id WHERE r.id=?", (self.current_review_id,))
            if res:
                content = res[0][0]
                display_text = f"📝 复习任务：\n\n{content}\n\n--------------------------\n💡 提示：请根据真实记忆情况点击下方按钮。"
                self.review_content_display.setPlainText(display_text)
        except Exception as e:
            print(f"加载复习内容出错: {e}")

    def show_add_review_dialog(self):
        title, ok1 = QInputDialog.getText(self, '添加复习', '请输入复习主题:')
        if ok1 and title:
            content, ok2 = QInputDialog.getMultiLineText(self, '添加复习', '请输入详细内容:')
            if ok2:
                add_review_task(title, content)
                QMessageBox.information(self, "成功", "已加入艾宾浩斯复习计划！")
                self.refresh_review_list() 

    def refresh_review_list(self):
        self.list_review.clear() 
        try:
            today_str = datetime.date.today().strftime('%Y-%m-%d')
            # 逻辑修复：只查出需要复习的（时间<=今天）
            rows = run_sql("SELECT r.id, t.content, r.next_review_date FROM review_plan r JOIN tasks t ON r.task_id = t.id WHERE r.next_review_date <= ? ORDER BY r.next_review_date ASC", (today_str,))
            for row in rows:
                preview = row[1].split('\n')[0][:15] # 取内容第一行作为标题预览
                item = QListWidgetItem(f"📅 待复习 | {preview}...")
                item.setData(Qt.UserRole, row[0]) 
                self.list_review.addItem(item)
        except Exception as e:
            print(f"刷新复习列表失败: {e}")

    def handle_review_mastered(self):
        """逻辑植入：真实验算并推进遗忘曲线进度"""
        if not self.current_review_id:
            QMessageBox.warning(self, "提示", "请先在左侧选择一个复习任务！")
            return
        
        res = run_sql("SELECT review_stage FROM review_plan WHERE id=?", (self.current_review_id,))
        if not res: return
        curr_stage = res[0][0]
        next_stage = curr_stage + 1

        if next_stage >= len(REVIEW_INTERVALS):
            run_sql("DELETE FROM review_plan WHERE id=?", (self.current_review_id,))
            QMessageBox.information(self, "大功告成", "恭喜！该知识点已完成所有复习周期，永久掌握！")
        else:
            days = REVIEW_INTERVALS[next_stage]
            next_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
            run_sql("UPDATE review_plan SET next_review_date=?, review_stage=? WHERE id=?",
                    (next_date, next_stage, self.current_review_id))
            QMessageBox.information(self, "继续保持", f"太棒了！已为你安排在 {days} 天后（{next_date}）再次复习。")
            
        self.refresh_review_list()
        self.review_content_display.clear()

    def handle_review_forget(self):
        """逻辑植入：重置复习状态到阶段0"""
        if not self.current_review_id: return
        next_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        run_sql("UPDATE review_plan SET next_review_date=?, review_stage=0 WHERE id=?", (next_date, self.current_review_id))
        QMessageBox.warning(self, "没关系", "失败是成功之母。已为你重新安排在明天复习该内容。")
        self.refresh_review_list()
        self.review_content_display.clear()

    def handle_remove_review_task(self):
        if not self.current_review_id: return
        reply = QMessageBox.question(self, '确认', '确定要将其永久移出复习计划吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            run_sql("DELETE FROM review_plan WHERE id=?", (self.current_review_id,))
            self.refresh_review_list()
            self.review_content_display.clear()

    # --- 模块 3: 文件整理 ---
    def setup_organizer_ui(self):
        layout = QVBoxLayout(self.tab_organizer)
        layout.setContentsMargins(40, 40, 40, 40)

        info = QLabel("📂 自动化文件归档系统")
        info.setStyleSheet("font-size: 24px; font-weight: bold; color: #2d5a4a;")
        layout.addWidget(info)
        layout.addWidget(QLabel("输入文件夹路径，程序将自动按文件类型（图片、文档、视频等）进行分类整理。"))

        path_box = QHBoxLayout()
        self.input_organize_path = QLineEdit()
        self.input_organize_path.setPlaceholderText("例如: C:/Users/Downloads")
        btn_browse = QPushButton("选择路径")
        btn_browse.clicked.connect(self.browse_path)
        path_box.addWidget(self.input_organize_path)
        path_box.addWidget(btn_browse)
        layout.addLayout(path_box)

        self.btn_run_organize = QPushButton("开始一键整理")
        self.btn_run_organize.setFixedHeight(50)
        self.btn_run_organize.setObjectName("btnPrimary")
        self.btn_run_organize.clicked.connect(self.run_file_organization)
        layout.addWidget(self.btn_run_organize)

        layout.addWidget(QLabel("整理日志："))
        self.list_organize_logs = QListWidget()
        layout.addWidget(self.list_organize_logs)

    def browse_path(self):
        p = QFileDialog.getExistingDirectory(self, "选择待整理的文件夹")
        if p: self.input_organize_path.setText(p)

    def run_file_organization(self):
        path = self.input_organize_path.text().strip()
        if not path or not os.path.isdir(path):
            QMessageBox.warning(self, "路径错误", "请选择有效的文件夹路径。")
            return

        self.list_organize_logs.clear()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            # 逻辑修复：完美接收 file_service 传回来的真实日志列表
            logs = self.file_service.start_organize(path)
            for log in logs:
                self.list_organize_logs.addItem(log)
        except Exception as e:
            self.list_organize_logs.addItem(f"❌ 运行故障: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()

    # --- 模块 4: 学习笔记 ---
    def setup_notes_ui(self):
        main_layout = QHBoxLayout(self.tab_notes)

        left_panel = QVBoxLayout()
        self.search_notes = QLineEdit()
        self.search_notes.setPlaceholderText("🔍 搜索笔记标题...")
        self.search_notes.textChanged.connect(self.refresh_notes_list)

        self.list_notes = QListWidget()
        self.list_notes.currentItemChanged.connect(self.load_selected_note)

        btn_new_note = QPushButton("+ 新建笔记")
        btn_new_note.setObjectName("btnPrimary") 
        btn_new_note.clicked.connect(self.create_new_note)

        left_panel.addWidget(self.search_notes); left_panel.addWidget(self.list_notes); left_panel.addWidget(btn_new_note)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(10) 

        self.input_note_title = QLineEdit()
        self.input_note_title.setPlaceholderText("在此输入笔记标题...")

        self.lbl_note_meta = QLabel("创建时间：— | 最后更新：—")
        self.lbl_note_meta.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-left: 5px;")

        self.note_editor = QTextEdit()
        self.note_editor.setPlaceholderText("在此输入笔记正文...")

        note_btn_layout = QHBoxLayout()

        self.btn_delete_note = QPushButton("🗑️ 删除笔记")
        self.btn_delete_note.setStyleSheet(DANGER_BUTTON)
        self.btn_delete_note.hide() 
        self.btn_delete_note.clicked.connect(self.delete_note)

        self.btn_save_note = QPushButton("保存笔记")
        self.btn_save_note.setObjectName("btnPrimary")
        self.btn_save_note.clicked.connect(self.save_note)

        note_btn_layout.addWidget(self.btn_delete_note); note_btn_layout.addWidget(self.btn_save_note)

        right_panel.addWidget(self.input_note_title); right_panel.addWidget(self.lbl_note_meta)
        right_panel.addWidget(self.note_editor); right_panel.addLayout(note_btn_layout) 

        main_layout.addLayout(left_panel, 1); main_layout.addLayout(right_panel, 3)

    def delete_note(self):
        if not self.current_note_id:
            QMessageBox.warning(self, "提示", "请先从左侧选择要删除的笔记。")
            return
        reply = QMessageBox.question(self, '确认删除', "确定要删除笔记吗？此操作不可撤销。", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                delete_note_by_id(self.current_note_id)
                QMessageBox.information(self, "成功", "笔记已删除。")
                self.refresh_notes_list()
                self._clear_note_editor()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除失败: {e}")

    def refresh_notes_list(self):
        try:
            keyword = self.search_notes.text().strip()
            data = get_notes_list(keyword)
            self.list_notes.clear()
            for row in data:
                item = QListWidgetItem(row[1])
                item.setData(Qt.UserRole, row[0])
                self.list_notes.addItem(item)
        except Exception as e:
            print(f"笔记加载失败: {e}")

    def load_selected_note(self, current, previous):
        if not current:
            self._clear_note_editor()
            self.btn_delete_note.hide()  
            return
        try:
            self.btn_delete_note.show()
            note_id = current.data(Qt.UserRole)
            row = get_note_by_id(note_id)
            if row:
                self.current_note_id = note_id
                self.input_note_title.setText(row[0])
                self.note_editor.setPlainText(row[1])
                self.lbl_note_meta.setText(f"创建：{fmt_cn_date(row[2])} | 最后更新：{fmt_cn_date(row[3])}")
                self.btn_save_note.setText("更新当前笔记")
        except Exception as e:
            QMessageBox.warning(self, "读取错误", f"无法加载: {e}")

    def create_new_note(self):
        self._clear_note_editor()
        self.input_note_title.setFocus()

    def save_note(self):
        title = self.input_note_title.text().strip() or "未命名笔记"
        content = self.note_editor.toPlainText().strip()
        try:
            save_or_update_note(self.current_note_id, title, content)
            QMessageBox.information(self, "成功", "笔记已安全存入数据库。")
            self.refresh_notes_list()
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))

    def _clear_note_editor(self):
        self.current_note_id = None
        self.input_note_title.clear(); self.note_editor.clear()
        self.lbl_note_meta.setText("创建时间：— | 最后更新：—")
        self.btn_save_note.setText("保存新笔记")

# ==========================================
# 9. 启动核心
# ==========================================
if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei UI", 10))
    window = SuperStudyApp()
    window.show()
    sys.exit(app.exec_())