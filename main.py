# -*- coding: utf-8 -*-
import sys
import os
import datetime
import random
import shutil
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QPixmap, QIcon

from db_manager import(
    run_sql,
    init_db,
    get_notes_list,
    get_note_by_id,
    save_or_update_note
)
# ==========================================
# 1. 环境初始化与依赖导入 (健壮性核心)
# ==========================================
# 解决 Qt 插件路径问题，防止在部分打包环境下崩溃
try:
    plugin_path = os.path.join(os.path.dirname(__import__('PyQt5').__file__), "Qt5", "plugins", "platforms")
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
except Exception:
    pass

from db_manager import (
    run_sql, init_db, get_notes_list,
    get_note_by_id, save_or_update_note
)
from app_styles import (
    QSS_APP_GLOBAL, QSS_REVIEW_CARD,
    QSS_REVIEW_CARD_SELECTED, build_tab_bar_qss, DANGER_BUTTON
)

# 尝试导入文件整理逻辑
try:
    from file_service import FileOrganizer
except ImportError:
    class FileOrganizer:
        def __init__(self): self.white_list = ['.JPG', '.PNG', '.PDF', '.DOCX']

        def start_organize(self, path): return ["⚠️ 未找到 file_service.py，当前仅为界面演示"]

# ==========================================
# 2. 通用工具函数与常量
# ==========================================
REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]  # 艾宾浩斯复习周期（天）


def fmt_cn_date(ymd: str) -> str:
    if not ymd or len(ymd) < 10: return "—"
    try:
        y, m, d = int(ymd[0:4]), int(ymd[5:7]), int(ymd[8:10])
        return f"{y}年{m}月{d}日"
    except (ValueError, IndexError):
        return ymd


# ==========================================
# 3. 自定义 UI 组件：复习卡片 (易维护：组件化)
# ==========================================
class ReviewCard(QWidget):
    def __init__(self, parent, plan_id, content, create_date, stage_num, next_review_date, mastery_level):
        super().__init__(parent)
        self.plan_id = plan_id
        self.content = content
        self.setObjectName("reviewCard")
        self.setStyleSheet(QSS_REVIEW_CARD)
        self._init_ui(content, create_date, stage_num, next_review_date, mastery_level)

    def _init_ui(self, content, create_date, stage_num, next_review_date, mastery_level):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)

        lbl_title = QLabel(content)
        lbl_title.setObjectName("reviewCardTitle")
        lbl_title.setWordWrap(True)

        lbl_meta = QLabel(f"加入：{fmt_cn_date(create_date)} | 阶段 {stage_num + 1}")
        lbl_meta.setObjectName("reviewCardMeta")

        lbl_next = QLabel(f"下次复习：{fmt_cn_date(next_review_date)}")
        lbl_next.setObjectName("reviewCardNext")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_meta)
        layout.addWidget(lbl_next)

    def mousePressEvent(self, event):
        # 健壮性：确保父窗口有处理方法
        if hasattr(self.window(), "_select_review_card"):
            self.window()._select_review_card(self.plan_id, self.content)
        super().mousePressEvent(event)


# ==========================================
# 4. 主程序类：布局构建
# ==========================================
class SuperStudyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StudyProgramPlus")
        self.resize(1150, 850)
        self.setStyleSheet(QSS_APP_GLOBAL)

        # 核心逻辑变量
        self.file_service = FileOrganizer()
        self.current_note_id = None
        self.selected_plan_id = None
        self.selected_plan_content = ""

        # 番茄钟变量
        self.time_left = 25 * 60
        self.is_running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.init_ui()

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
        title_box.addWidget(m_title);
        title_box.addWidget(s_title)

        layout.addLayout(title_box)
        layout.addStretch()

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

        # 定义四张页面的 Container
        self.tab_pomo = QWidget()
        self.tab_review = QWidget()
        self.tab_organizer = QWidget()
        self.tab_notes = QWidget()

        self.tabs.addTab(self.tab_pomo, "番茄专注")
        self.tabs.addTab(self.tab_review, "智能复习")
        self.tabs.addTab(self.tab_organizer, "文件管理")
        self.tabs.addTab(self.tab_notes, "学习笔记")

        main_layout.addWidget(self.tabs)

        # 执行各模块具体的 UI 绘制（具体逻辑见第二部分消息）
        self.setup_pomo_ui()
        self.setup_review_tab()
        self.setup_organizer_ui()
        self.setup_notes_ui()

    def load_review_content(self, current, previous):
        """当点击左侧复习列表项时，把详细内容显示在右边的文本框里"""
        # 1. 安全检查：如果没选中任何东西，清空右侧并返回
        if not current:
            self.review_content_display.clear()
            return

        try:
            # 2. 获取当前选中项的文字内容
            # 这里先用最简单的逻辑：直接读取列表显示的文字
            task_text = current.text()

            # 3. 把内容显示到右侧的 QTextEdit 中
            # 我们稍微排个版，让它好看一点
            display_text = f"📝 复习任务：\n\n{task_text}\n\n"
            display_text += "--------------------------\n"
            display_text += "💡 提示：请根据记忆情况点击下方按钮进行反馈。"

            self.review_content_display.setPlainText(display_text)

        except Exception as e:
            print(f"加载复习内容出错: {e}")
        # ==========================================
        # 5. 模块一：番茄专注 (Pomodoro) - 完整逻辑
        # ==========================================
    def setup_pomo_ui(self):
        layout = QVBoxLayout(self.tab_pomo)
        layout.setAlignment(Qt.AlignCenter)

        # 时间显示
        self.lbl_time = QLabel("25:00")
        self.lbl_time.setObjectName("TimerDisplay")  # 对应 QSS 样式
        self.lbl_time.setAlignment(Qt.AlignCenter)
        self.lbl_time.setStyleSheet("font-size: 120px; font-weight: bold; color: #2d5a4a; margin: 20px;")

        # 按钮容器
        btn_layout = QHBoxLayout()
        self.btn_start_pomo = QPushButton("开始专注")
        self.btn_start_pomo.setFixedSize(200, 60)
        self.btn_start_pomo.setObjectName("btnPrimary")
        self.btn_start_pomo.clicked.connect(self.toggle_timer)

        btn_reset = QPushButton("重置")
        btn_reset.setFixedSize(120, 60)
        btn_reset.clicked.connect(self.reset_timer)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_start_pomo)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()

        layout.addStretch()
        layout.addWidget(self.lbl_time)
        layout.addLayout(btn_layout)
        layout.addStretch()    

    def toggle_timer(self):
        if not self.is_running:
            self.timer.start(1000)
            self.btn_start_pomo.setText("暂停")
            self.btn_start_pomo.setStyleSheet("background-color: #e67e22;")  # 橙色表示进行中
        else:
            self.timer.stop()
            self.btn_start_pomo.setText("继续专注")
            self.btn_start_pomo.setStyleSheet("")  # 恢复 QSS 默认
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
            QMessageBox.information(self, "时间到", "太棒了！你完成了一个番茄钟，休息一下吧。")
            self.reset_timer()

    # ==========================================
    # 6. 模块二：智能复习 (Ebbinghaus) - 完整逻辑
    # ==========================================
    def setup_review_tab(self):
        """智能复习模块 UI 布局 - 已按要求重排"""
        main_layout = QHBoxLayout(self.tab_review)

        # 1. 左侧任务列表区
        left_panel = QVBoxLayout()

        # 【功能添加】左侧顶部的按钮行（刷新 + 添加）
        left_btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("🔄 刷新列表")
        # 如果你之前没有在全局 QSS 里定义 btnPrimary，可以先注掉下面这行
        self.btn_refresh.setObjectName("btnPrimary")

        self.btn_add_review = QPushButton("+ 添加复习")
        self.btn_add_review.setObjectName("btnPrimary")

        left_btn_layout.addWidget(self.btn_refresh)
        left_btn_layout.addWidget(self.btn_add_review)

        self.list_review = QListWidget()
        # 绑定：点击左侧列表，右侧显示内容
        self.list_review.currentItemChanged.connect(self.load_review_content)

        left_panel.addLayout(left_btn_layout)
        left_panel.addWidget(self.list_review)

        # 2. 右侧操作区 (改为你要求的上下结构)
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(10, 0, 10, 0)

        # 【上方】详细内容预览区域 (QTextEdit)
        self.review_content_display = QTextEdit()
        self.review_content_display.setReadOnly(True)
        self.review_content_display.setPlaceholderText("💡 请从左侧列表中选择一个复习任务...")
        # 设置一点内部样式，让它看起来更舒服
        self.review_content_display.setStyleSheet("""
            background-color: #ffffff; 
            border: 1px solid #d4e4da; 
            border-radius: 15px; 
            padding: 10px;
        """)

        # 【下方】操作按钮横向紧凑排列
        op_btn_layout = QHBoxLayout()
        op_btn_layout.setSpacing(10)  # 按钮之间的间距

        # 创建那三个核心按钮
        self.btn_mastered = QPushButton("✅ 这一阶段已掌握")
        self.btn_forget = QPushButton("❌ 记不清了，重来")
        self.btn_remove_task = QPushButton("🗑️ 移出复习计划")

        # 给“移出”按钮单独加个红色样式（可选）
        self.btn_remove_task.setStyleSheet("background-color: #ffab91; color: white; border-radius: 15px;")

        op_btn_layout.addWidget(self.btn_mastered)
        op_btn_layout.addWidget(self.btn_forget)
        op_btn_layout.addWidget(self.btn_remove_task)

        # 按照 7:3 的比例分配空间
        right_panel.addWidget(self.review_content_display, 7)
        right_panel.addLayout(op_btn_layout, 3)

        # 3. 最后将左右面板加入主布局 (1:2 比例)
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)

        # --- 信号绑定 ---
        self.btn_refresh.clicked.connect(self.refresh_review_list)
        self.btn_add_review.clicked.connect(self.show_add_review_dialog)
        # 这里的函数名需要和你代码里实际处理“掌握/重来”的函数名一致
        self.btn_mastered.clicked.connect(self.handle_review_mastered)
        self.btn_forget.clicked.connect(self.handle_review_forget)
        self.btn_remove_task.clicked.connect(self.handle_remove_review_task)

    def refresh_review_table(self):
        """清空并重新加载所有复习卡片"""
        # 清除现有组件
        for i in reversed(range(self.review_flow_layout.count())):
            self.review_flow_layout.itemAt(i).widget().setParent(None)

        sql = """SELECT r.id, t.content, t.create_date, r.review_stage, r.next_review_date, r.mastery_level 
                    FROM review_plan r JOIN tasks t ON r.task_id = t.id 
                    ORDER BY r.next_review_date ASC"""
        data = run_sql(sql)

        if not data:
            self.review_flow_layout.addWidget(QLabel("目前没有复习任务，快去添加吧！"))
            self.review_flow_layout.addWidget(QLabel("目前没有复习任务，快去添加吧！"))
        else:
            for row in data:
                card = ReviewCard(self, row[0], row[1], row[2], row[3], row[4], row[5])
                self.review_flow_layout.addWidget(card)

        self.selected_plan_id = None
        self.lbl_selected_task.setText("请选择左侧卡片")

    def _select_review_card(self, plan_id, content):
        self.selected_plan_id = plan_id
        self.selected_plan_content = content
        self.lbl_selected_task.setText(f"当前选中：\n{content}")

    def update_mastery(self, status):
        if not self.selected_plan_id:
            QMessageBox.warning(self, "提示", "请先选择一张复习卡片！")
            return

        res = run_sql("SELECT review_stage FROM review_plan WHERE id=?", (self.selected_plan_id,))
        curr_stage = res[0][0]

        if status == "掌握":
            next_stage = curr_stage + 1
            if next_stage >= len(REVIEW_INTERVALS):
                QMessageBox.information(self, "大功告成", "该任务已完成所有复习阶段，将自动移出计划！")
                run_sql("DELETE FROM review_plan WHERE id=?", (self.selected_plan_id,))
            else:
                days = REVIEW_INTERVALS[next_stage]
                next_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
                run_sql("UPDATE review_plan SET next_review_date=?, review_stage=? WHERE id=?",
                        (next_date, next_stage, self.selected_plan_id))
        else:  # 重学
            next_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            run_sql("UPDATE review_plan SET next_review_date=?, review_stage=0 WHERE id=?",
                    (next_date, self.selected_plan_id))

        self.refresh_review_table()

    def remove_from_curve(self):
        if not self.selected_plan_id: return
        if QMessageBox.question(self, "确认", "确定要将此项移出复习计划吗？") == QMessageBox.Yes:
            run_sql("DELETE FROM review_plan WHERE id=?", (self.selected_plan_id,))
            self.refresh_review_table()

        # ==========================================
        # 7. 模块三：文件整理 (Organizer) - 完整逻辑
        # ==========================================

    def setup_organizer_ui(self):
        layout = QVBoxLayout(self.tab_organizer)
        layout.setContentsMargins(40, 40, 40, 40)

        info = QLabel("📂 自动化文件归档系统")
        info.setStyleSheet("font-size: 24px; font-weight: bold; color: #2d5a4a;")
        layout.addWidget(info)

        desc = QLabel("输入文件夹路径，程序将自动按文件类型（图片、文档、视频等）进行分类整理。")
        layout.addWidget(desc)

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
            logs = self.file_service.start_organize(path)
            for log in (logs or ["✅ 整理任务已尝试执行"]):
                self.list_organize_logs.addItem(log)
        except Exception as e:
            self.list_organize_logs.addItem(f"❌ 运行故障: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()

    # ==========================================
    # 8. 模块四：学习笔记 (Notes) - 完整逻辑
    # ==========================================
    def setup_notes_ui(self):
        """笔记模块 UI 布局 - 已修复布局不显示的问题"""
        # 0. 核心：确保这一行存在，它是通往主界面的门
        if not hasattr(self, 'tab_notes'):
            self.tab_notes = QWidget()
            self.tabs.addTab(self.tab_notes, "📓 学习笔记")

        # 创建主布局（水平：左边列表，右边编辑）
        main_layout = QHBoxLayout(self.tab_notes)

        # 1. 左侧列表区
        left_panel = QVBoxLayout()
        self.search_notes = QLineEdit()
        self.search_notes.setPlaceholderText("🔍 搜索笔记标题...")
        self.search_notes.textChanged.connect(self.refresh_notes_list)

        self.list_notes = QListWidget()
        self.list_notes.currentItemChanged.connect(self.load_selected_note)

        btn_new_note = QPushButton("+ 新建笔记")
        btn_new_note.setObjectName("btnPrimary") # 保持绿色风格
        btn_new_note.clicked.connect(self.create_new_note)

        left_panel.addWidget(self.search_notes)
        left_panel.addWidget(self.list_notes)
        left_panel.addWidget(btn_new_note)

        # 2. 右侧编辑区
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10) 

        self.input_note_title = QLineEdit()
        self.input_note_title.setPlaceholderText("在此输入笔记标题...")
        self.input_note_title.setObjectName("noteTitleInput")

        self.lbl_note_meta = QLabel("创建时间：— | 最后更新：—")
        self.lbl_note_meta.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-left: 5px;")

        self.note_editor = QTextEdit()
        self.note_editor.setPlaceholderText("在此输入笔记正文...")
        self.note_editor.setObjectName("noteEditor")

        # 按钮水平布局
        note_btn_layout = QHBoxLayout()

        # 【修复重复定义】只保留一个删除按钮定义
        self.btn_delete_note = QPushButton("🗑️ 删除笔记")
        self.btn_delete_note.setStyleSheet(DANGER_BUTTON)
        self.btn_delete_note.hide()  # 初始隐藏
        self.btn_delete_note.clicked.connect(self.delete_note)

        self.btn_save_note = QPushButton("保存笔记")
        self.btn_save_note.setObjectName("btnPrimary")
        self.btn_save_note.clicked.connect(self.save_note)

        note_btn_layout.addWidget(self.btn_delete_note)
        note_btn_layout.addWidget(self.btn_save_note)

        right_panel.addWidget(self.input_note_title)
        right_panel.addWidget(self.lbl_note_meta)
        right_panel.addWidget(self.note_editor)
        right_panel.addLayout(note_btn_layout) 

        # --- 【最关键的修改在这里！】 ---
        # 必须把左右两个面板加入到 main_layout 中，界面才会显示！
        main_layout.addLayout(left_panel, 1)  # 左边占 1 份宽度
        main_layout.addLayout(right_panel, 3) # 右边占 3 份宽度

    def delete_note(self):
        """删除当前选中的笔记"""
        if not self.current_note_id:
            QMessageBox.warning(self, "提示", "请先从左侧列表选择一篇要删除的笔记。")
            return

        # 弹出二次确认，防止误删
        reply = QMessageBox.question(self, '确认删除',
                                     f"确定要删除笔记吗？此操作不可撤销。",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # 1. 调用数据库删除接口 (注意：你需要在 db_manager 里加上这个函数)
                from db_manager import delete_note_by_id
                delete_note_by_id(self.current_note_id)

                # 2. 界面反馈
                QMessageBox.information(self, "成功", "笔记已删除。")

                # 3. 刷新列表并清空编辑器
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
            print(f"笔记列表加载失败: {e}")

    def load_selected_note(self, current, previous):
        # 1. 第一种情况：如果没有选中任何项（比如点击了空白处）
        if not current:
            self._clear_note_editor()
            self.btn_delete_note.hide()  # 【新增】隐藏删除按钮，因为没东西可删
            return

        # 2. 第二种情况：选中了某篇笔记
        try:
            # --- 【新增：在这里把删除按钮变出来】 ---
            self.btn_delete_note.show()

            # 以下是你原有的读取逻辑
            note_id = current.data(Qt.UserRole)
            row = get_note_by_id(note_id)
            if row:
                self.current_note_id = note_id
                self.input_note_title.setText(row[0])
                self.note_editor.setPlainText(row[1])
                # 注意：确保你的代码里定义了 fmt_cn_date 函数
                self.lbl_note_meta.setText(f"创建：{fmt_cn_date(row[2])} | 最后更新：{fmt_cn_date(row[3])}")
                self.btn_save_note.setText("更新当前笔记")

        except Exception as e:
            QMessageBox.warning(self, "读取错误", f"无法加载笔记: {e}")

    def create_new_note(self):
        self._clear_note_editor()
        self.input_note_title.setFocus()

    def save_note(self):
        title = self.input_note_title.text().strip()
        content = self.note_editor.toPlainText().strip()
        if not title: title = "未命名笔记"

        try:
            is_new = save_or_update_note(self.current_note_id, title, content)
            QMessageBox.information(self, "保存成功", "笔记内容已写入数据库。")
            self.refresh_notes_list()
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))

    def _clear_note_editor(self):
        self.current_note_id = None
        self.input_note_title.clear()
        self.note_editor.clear()
        self.lbl_note_meta.setText("创建时间：— | 最后更新：—")
        self.btn_save_note.setText("保存新笔记")

    def handle_delete_note(self):
        # 弹出二次确认，防止手残
        reply = QMessageBox.question(self, '确认删除', "笔记删了就找不回来咯，确定吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 获取当前选中的笔记 ID (假设你存储在 self.current_note_id)
            if hasattr(self, 'current_note_id'):
                self.db.delete_note_by_id(self.current_note_id)
                self.refresh_note_list()  # 刷新列表
                self.clear_note_editor()  # 清空编辑器
                self.delete_note_btn.hide()  # 删完就藏起来

    def show_add_review_dialog(self):
        """弹出添加复习任务的对话框"""
        title, ok1 = QInputDialog.getText(self, '添加复习', '请输入复习主题:')
        if ok1 and title:
            content, ok2 = QInputDialog.getMultiLineText(self, '添加复习', '请输入详细内容:')
            if ok2:
                # 调用你数据库里的增加函数
                from db_manager import add_review_task
                add_review_task(title, content)
                QMessageBox.information(self, "成功", "已加入艾宾浩斯复习计划！")
                self.refresh_review_list()  # 记得刷新列表

    def refresh_review_list(self):
        """刷新左侧复习任务列表"""
        self.list_review.clear() # 先清空旧的
        try:
            # 这里调用数据库获取复习计划
            # 假设你的 db_manager 里有 get_review_plans 函数
            from db_manager import run_sql
            rows = run_sql("SELECT id, task_id, next_review_date FROM review_plan ORDER BY next_review_date ASC")
            
            for row in rows:
                # 简单展示任务ID和时间，后期你可以根据 task_id 关联查询具体内容
                item = QListWidgetItem(f"📅 待复习 | 任务#{row[1]} | 时间:{row[2]}")
                item.setData(Qt.UserRole, row[0]) # 偷偷藏进 ID，方便后面点击
                self.list_review.addItem(item)
                
        except Exception as e:
            print(f"刷新复习列表失败: {e}")

    def handle_review_mastered(self):
        """点击‘已掌握’的逻辑"""
        QMessageBox.information(self, "加油", "太棒了！该任务将进入下一个复习周期。")
        # 这里以后要写更新数据库 review_stage 的逻辑

    def handle_review_forget(self):
        """点击‘重来’的逻辑"""
        QMessageBox.warning(self, "没关系", "没关系，我们会重新安排复习频率。")

    def handle_remove_review_task(self):
        """点击‘移出’的逻辑"""
        reply = QMessageBox.question(self, '确认', '确定要停止复习这个任务吗？',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 这里写从数据库删除 review_plan 的逻辑
            self.refresh_review_list()
# ==========================================
# 9. 程序入口 (Main Entry)
# ==========================================
if __name__ == "__main__":
    # 初始化数据库
    init_db()

    app = QApplication(sys.argv)
    # 设置全局 UI 字体
    font = QFont("Microsoft YaHei UI", 10)
    app.setFont(font)

    # 启动主窗口
    window = SuperStudyApp()
    window.show()

    sys.exit(app.exec_())
