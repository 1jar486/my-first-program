
import sys
import os
import datetime
import random
import PyQt5

# 1. 终极护甲：解决插件初始化失败报错
plugin_path = os.path.join(os.path.dirname(PyQt5.__file__), "Qt5", "plugins", "platforms")
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QPixmap
from db_manager import run_sql, init_db
from app_styles import (
    QSS_APP_GLOBAL,
    QSS_REVIEW_CARD,
    QSS_REVIEW_CARD_SELECTED,
    build_tab_bar_qss,
)



# 可选：放置 logo.png 用于顶栏装饰
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def fmt_cn_date(ymd: str) -> str:
    """将 YYYY-MM-DD 格式化为中文年月日。"""
    if not ymd or len(ymd) < 10:
        return ymd or "—"
    try:
        y, m, d = int(ymd[0:4]), int(ymd[5:7]), int(ymd[8:10])
        return f"{y}年{m}月{d}日"
    except (ValueError, IndexError):
        return ymd

# 可配置：番茄图标（没有图片会自动使用 🍅 兜底）
TOMATO_ICON_PATH = os.path.join(ASSETS_DIR, "tomato.png")
TOMATO_EMOJI = "🍅"

# 正向鼓励话语：名人名言 + 鸡汤（都保持正能量）
ENCOURAGEMENTS = [
    "成功不是终点，失败也并不致命。关键在于你是否愿意继续前进。",
    "行动胜于言辞。先启动，再优化。",
    "把每一天都当成一次小小的训练，你会惊喜地变强。",
    "你今天做的每一步，都会在未来的某个瞬间回报你。",
    "我没有失败，我只是找到了 10000 种行不通的方法。继续试试！",
    "成功的秘诀是把宏大的目标拆成每天都能完成的小任务。",
    "保持饥饿，保持愚蠢；继续学习，继续创造。",
    "只要不停止，哪怕走得慢，也总是在向前。",
]


def get_encouragement() -> str:
    """随机挑一句鼓励话语。"""
    return random.choice(ENCOURAGEMENTS)


class ReviewCard(QWidget):
    """到期复习的“卡片”展示，用于替代表格的选中逻辑。"""

    def __init__(self, parent, plan_id: int, content: str, create_date: str,
                 stage_num: int, next_review_date: str, mastery_level: str):
        super().__init__(parent)
        self.plan_id = plan_id
        self.content = content

        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("reviewCard")
        self.setStyleSheet(QSS_REVIEW_CARD)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        top = QLabel(content)
        top.setObjectName("reviewCardTitle")
        top.setWordWrap(True)
        layout.addWidget(top)

        meta1 = QLabel(f"加入：{fmt_cn_date(create_date)}")
        meta1.setObjectName("reviewCardMeta")
        layout.addWidget(meta1)

        meta2 = QLabel(f"当前阶段：阶段 {stage_num + 1}")
        meta2.setObjectName("reviewCardMeta")
        layout.addWidget(meta2)

        next_meta = QLabel(f"下次复习：{fmt_cn_date(next_review_date)}")
        next_meta.setObjectName("reviewCardNext")
        layout.addWidget(next_meta)

        mastery = mastery_level or ""
        mastery_label = QLabel(f"掌握：{mastery}")
        mastery_label.setObjectName("reviewCardMeta")
        layout.addWidget(mastery_label)

    def mousePressEvent(self, event):
        # 点击卡片：通知父窗口“选中”
        win = self.window()
        if hasattr(win, "_select_review_card"):
            win._select_review_card(self.plan_id, self.content)
        super().mousePressEvent(event)

# 艾宾浩斯复习间隔（天）
REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]

class PomodoroCard(QFrame):
    """右侧 2/3 区域的现代感番茄钟卡片"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PomodoroCard") # 必须设置，否则没样式
        self.setFixedSize(450, 500) 

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 40)

        # 顶部番茄图标 (如果暂时没图片，会显示红色的圆圈)
        self.icon_label = QLabel("🍅") 
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 80px;") 

        # 中间时间数字
        self.timer_label = QLabel("25:00")
        self.timer_label.setObjectName("TimerDisplay") # 样式钩子
        self.timer_label.setAlignment(Qt.AlignCenter)

        # 开始按钮
        self.start_btn = QPushButton("开始专注")
        self.start_btn.setObjectName("StartFocusBtn") # 样式钩子
        self.start_btn.setCursor(Qt.PointingHandCursor)

        layout.addStretch()
        layout.addWidget(self.icon_label)
        layout.addWidget(self.timer_label)
        layout.addSpacing(20)
        layout.addWidget(self.start_btn, alignment=Qt.AlignCenter)
        layout.addStretch()

class SuperStudyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Study+ 学习助手")
        self._scalable_buttons = []
        self._centered = False
        screen = QApplication.primaryScreen().availableGeometry()
        # 长方形主窗：约占屏幕约 2/3 宽、2/3 高
        w = max(640, int(screen.width() * 2 / 3))
        h = max(480, int(screen.height() * 2 / 3))
        self.resize(w, h)
        self.setMinimumSize(560, 420)
        self.setStyleSheet(QSS_APP_GLOBAL)

        # 番茄钟核心变量
        self.work_time = 25 * 60
        self.time_left = self.work_time
        self.is_running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.init_ui()

    def init_ui(self):
        """初始化整体标签页布局"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        main_layout.addWidget(self._build_app_header())
        main_layout.setSpacing(12)

        self.tabs = QTabWidget()
        self.tab_pomo = QWidget()
        self.tab_review = QWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self.tab_pomo, "番茄专注")
        self.tabs.addTab(self.tab_review, "智能复习")

        main_layout.setContentsMargins(16, 16, 16, 18)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.tabs)
        self.setup_pomodoro_ui()
        self.refresh_pomodoro_stats()
        self.setup_review_ui()  # UI架子先搭好，逻辑在第二部分
        self.refresh_review_table()

    def _build_app_header(self):
        """顶栏：品牌文案 + 可选 logo 图"""
        header = QWidget()
        header.setObjectName("appHeader")
        header.setMinimumHeight(88)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(22, 18, 22, 18)
        hl.setSpacing(16)

        icon_lbl = QLabel()
        icon_lbl.setAlignment(Qt.AlignCenter)
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        logo_ok = False
        if os.path.isfile(logo_path):
            pix = QPixmap(logo_path)
            if not pix.isNull():
                icon_lbl.setPixmap(pix.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                icon_lbl.setFixedSize(64, 64)
                logo_ok = True
        if not logo_ok:
            icon_lbl.setText("\u2728")
            icon_lbl.setFont(QFont("Segoe UI Emoji", 36))
            icon_lbl.setFixedSize(64, 64)
        hl.addWidget(icon_lbl, 0, Qt.AlignVCenter)

        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        title = QLabel("Study+ 学习助手")
        title.setObjectName("heroTitle")
        sub = QLabel("专注当下 · 科学复习 · 进度看得见")
        sub.setObjectName("heroSubtitle")
        sub.setWordWrap(True)
        text_col.addWidget(title)
        text_col.addWidget(sub)
        hl.addLayout(text_col, 1)

        tag = QLabel("今日也要进步一点点")
        tag.setObjectName("headerTagPill")
        tag.setAlignment(Qt.AlignCenter)
        hl.addWidget(tag, 0, Qt.AlignVCenter | Qt.AlignRight)

        return header

    def showEvent(self, event):
        super().showEvent(event)
        if not self._centered:
            self._centered = True
            fg = self.frameGeometry()
            c = QApplication.primaryScreen().availableGeometry().center()
            fg.moveCenter(c)
            self.move(fg.topLeft())
        self._apply_ui_scale()

    def _apply_ui_scale(self):
        """按窗口尺寸统一按钮、输入框、表格行高与字号，保持比例协调。"""
        w, h = max(self.width(), 400), max(self.height(), 300)
        s = max(0.9, min(1.28, (w / 1100.0 + h / 820.0) * 0.52))
        btn_h = max(40, int(44 * s))
        fs = max(13, int(14 * s))
        f_btn = QFont("Microsoft YaHei UI", fs, QFont.DemiBold)
        f_field = QFont("Microsoft YaHei UI", fs)
        for b in self._scalable_buttons:
            bh = btn_h
            if b.objectName() in ("btnPrimary", "btnReset"):
                bh = max(btn_h, int(52 * s))
            b.setMinimumHeight(bh)
            b.setFont(f_btn)
            if b.objectName() in ("btnPrimary", "btnReset"):
                b.setMinimumWidth(max(168, int(228 * s)))
        if hasattr(self, "input_knowledge"):
            self.input_knowledge.setMinimumHeight(btn_h)
            self.input_knowledge.setFont(f_field)
        if hasattr(self, "lbl_status"):
            self.lbl_status.setFont(QFont("Microsoft YaHei UI", max(13, int(14 * s))))
        if hasattr(self, "lbl_today_done"):
            self.lbl_today_done.setFont(QFont("Microsoft YaHei UI", max(12, int(12 * s))))
        if not hasattr(self, "tabs"):
            return
        tab_fs = max(14, int(15 * s))
        th = max(40, int(42 * s))
        self.tabs.setStyleSheet(build_tab_bar_qss(th, tab_fs))

    def _sync_pomo_timer_scale(self):
        """按窗口高度同步计时数字与番茄图标（需在 QSS 中勿对 lblPomoTime 写死 font-size）。"""
        if not hasattr(self, "lbl_time"):
            return
        h = max(1, self.height())
        pt = max(118, min(230, int(h * 0.24)))
        self.lbl_time.setFont(QFont("Segoe UI", pt, QFont.Bold))
        if not hasattr(self, "lbl_tomato_icon"):
            return
        icon_size = max(96, int(pt * 0.88))
        self.lbl_tomato_icon.setFixedSize(icon_size, icon_size)
        if getattr(self, "_tomato_pix", None) is not None:
            self.lbl_tomato_icon.setPixmap(
                self._tomato_pix.scaled(
                    icon_size,
                    icon_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            self.lbl_tomato_icon.setFont(
                QFont("Segoe UI Emoji", max(30, int(icon_size * 0.6)))
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._sync_pomo_timer_scale()
        # 计时模块整体上移约 1/4 个“视觉台阶”（相对窗口高度）
        if hasattr(self, "_pomo_timer_wrap"):
            up = int(self.height() * 0.06)
            self._pomo_timer_wrap.setContentsMargins(0, -up, 0, 0)
        self._apply_ui_scale()

    def setup_pomodoro_ui(self):
        """番茄钟：右侧 2/3 区域居中展示计时；状态文案固定在页底。"""
        outer = QVBoxLayout(self.tab_pomo)
        outer.setContentsMargins(0, 0, 0, 0)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 24)

        kicker = QLabel("POMODORO")
        kicker.setObjectName("sectionKicker")
        layout.addWidget(kicker)
        title = QLabel("番茄专注")
        title.setObjectName("heroTitle")
        layout.addWidget(title)
        desc = QLabel("标准 25 分钟倒计时，结束自动记入专注日志。\n放下手机，只做好眼前这一件事。")
        desc.setObjectName("pomoBody")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.lbl_today_done = QLabel("今日已完成：0 次")
        self.lbl_today_done.setObjectName("pomoToday")
        self.lbl_today_done.setAlignment(Qt.AlignLeft)
        self.lbl_today_done.setWordWrap(True)
        layout.addWidget(self.lbl_today_done)

        # 计时器：番茄图标 + 时间数字
        self.lbl_tomato_icon = QLabel()
        self.lbl_tomato_icon.setAlignment(Qt.AlignCenter)
        self._tomato_pix = None
        if os.path.isfile(TOMATO_ICON_PATH):
            pix = QPixmap(TOMATO_ICON_PATH)
            if not pix.isNull():
                self._tomato_pix = pix
                self.lbl_tomato_icon.setPixmap(
                    pix.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
                self.lbl_tomato_icon.setFixedSize(120, 120)

        if self._tomato_pix is None:
            self.lbl_tomato_icon.setText(TOMATO_EMOJI)
            self.lbl_tomato_icon.setFont(QFont("Segoe UI Emoji", 56))
            self.lbl_tomato_icon.setFixedSize(120, 120)

        self.lbl_time = QLabel("25:00")
        self.lbl_time.setObjectName("lblPomoTime")
        self.lbl_time.setAlignment(Qt.AlignCenter)
        self.lbl_time.setFont(QFont("Segoe UI", 128, QFont.Bold))
        self.lbl_time.setMinimumHeight(152)

        self._time_row_layout = QHBoxLayout()
        self._time_row_layout.setContentsMargins(0, 0, 0, 0)
        self._time_row_layout.setSpacing(16)
        self._time_row_layout.addWidget(self.lbl_tomato_icon)
        self._time_row_layout.addWidget(self.lbl_time)

        self.lbl_status = QLabel("准备好进入心流状态了吗？")
        self.lbl_status.setObjectName("pomoStatus")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setWordWrap(True)

        self.btn_start = QPushButton("开始专注")
        self.btn_start.setObjectName("btnPrimary")
        self.btn_reset = QPushButton("放弃本轮")
        self.btn_reset.setObjectName("btnReset")
        self.btn_reset.setEnabled(False)
        self.btn_start.clicked.connect(self.toggle_timer)
        self.btn_reset.clicked.connect(self.reset_timer)
        self._scalable_buttons.extend([self.btn_start, self.btn_reset])

        # 时间 + 按钮（状态不跟在这里，改到页面最底部）
        center_col = QVBoxLayout()
        center_col.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        center_col.setSpacing(16)
        self._pomo_timer_wrap = QWidget()
        self._pomo_timer_wrap.setObjectName("pomoTimerCard")
        tw = QVBoxLayout(self._pomo_timer_wrap)
        tw.setContentsMargins(20, 18, 20, 20)
        tw.setSpacing(18)
        tw.addLayout(self._time_row_layout)
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(16)
        btn_row.addWidget(self.btn_start, 1, Qt.AlignLeft)
        btn_row.addWidget(self.btn_reset, 1, Qt.AlignRight)
        tw.addLayout(btn_row)
        center_col.addWidget(self._pomo_timer_wrap)

        # 右侧约 2/3：计时块水平居中；下方留白由 stretch 吃掉，整体视觉偏上
        timer_area = QHBoxLayout()
        timer_area.setContentsMargins(0, 0, 0, 0)
        timer_area.addStretch(1)
        right_stack = QVBoxLayout()
        right_stack.setContentsMargins(0, 0, 0, 0)
        right_stack.setSpacing(0)
        right_stack.addLayout(center_col, 0)
        right_stack.addStretch(1)
        timer_area.addLayout(right_stack, 2)
        layout.addLayout(timer_area, 1)

        tip = QLabel("小提示：中途离开可点「放弃本轮」，本轮不计入完成。")
        tip.setObjectName("pomoTip")
        tip.setWordWrap(True)
        layout.addWidget(tip)

        layout.addWidget(self.lbl_status, 0, Qt.AlignBottom)

        outer.addWidget(inner)
        QTimer.singleShot(0, self._sync_pomo_timer_scale)

    def toggle_timer(self):
        """切换计时状态"""
        if not self.is_running:
            self.timer.start(1000)
            self.is_running = True
            self.btn_start.setText("暂停")
            self.btn_reset.setEnabled(True)
            self.lbl_status.setText("专注中…")
        else:
            self.timer.stop()
            self.is_running = False
            self.btn_start.setText("继续")
            self.lbl_status.setText("已暂停")

    def refresh_pomodoro_stats(self):
        """刷新番茄钟今日完成次数。"""
        if not hasattr(self, "lbl_today_done"):
            return
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        res = run_sql("SELECT COUNT(*) FROM pomodoro_logs WHERE focus_date=?", (today,))
        count = res[0][0] if res else 0
        self.lbl_today_done.setText(f"今日已完成：{count} 次")

    def update_timer(self):
        """每秒更新时间显示"""
        if self.time_left > 0:
            self.time_left -= 1
            mins, secs = divmod(self.time_left, 60)
            self.lbl_time.setText(f"{mins:02d}:{secs:02d}")

        if self.time_left <= 0:
            self.timer.stop()
            self.is_running = False
            try:
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                run_sql("INSERT INTO pomodoro_logs (focus_date, focus_minutes) VALUES (?, ?)", (today, 25))
            except Exception as e:
                print(f"数据库记录失败: {e}")

            self.refresh_pomodoro_stats()
            quote = get_encouragement()
            QMessageBox.information(self, "时间到", f"恭喜完成一个番茄钟！\n{quote}")
            self.reset_timer()

    def reset_timer(self):
        """重置计时器逻辑"""
        self.timer.stop()
        self.is_running = False
        self.time_left = self.work_time  # 确保 work_time 已在 __init__ 定义
        self.lbl_time.setText("25:00")
        self.btn_start.setText("开始专注")
        self.btn_reset.setEnabled(False)
        self.lbl_status.setText("准备好进入心流状态了吗？")
    # ================== 界面：搭建复习页面的“皮囊” ==================
    def setup_review_ui(self):
        """复习页：纵向排布 + 可滚动"""
        outer = QVBoxLayout(self.tab_review)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 24)

        rk = QLabel("SPACED REVIEW")
        rk.setObjectName("sectionKicker")
        layout.addWidget(rk)
        rt = QLabel("智能复习")
        rt.setObjectName("heroTitle")
        layout.addWidget(rt)
        banner = QLabel(
            "按艾宾浩斯间隔（1→2→4→7→15→30 天）安排复习；列表中为「今天及之前到期」的条目。"
        )
        banner.setObjectName("reviewBanner")
        banner.setWordWrap(True)
        layout.addWidget(banner)

        input_group = QGroupBox("录入新学内容")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(12)
        self.input_knowledge = QLineEdit()
        self.input_knowledge.setPlaceholderText("输入知识点名称，回车也可提交")
        self.input_knowledge.returnPressed.connect(self.add_knowledge)
        self.btn_add_knowledge = QPushButton("加入记忆曲线")
        self.btn_add_knowledge.clicked.connect(self.add_knowledge)
        input_layout.addWidget(self.input_knowledge)
        input_layout.addWidget(self.btn_add_knowledge)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        self._scalable_buttons.append(self.btn_add_knowledge)

        list_title = QLabel("今日待复习")
        list_title.setObjectName("reviewListTitle")
        layout.addWidget(list_title)

        self.lbl_review_count = QLabel("到期：0 条")
        self.lbl_review_count.setObjectName("reviewCount")
        self.lbl_review_count.setWordWrap(True)
        layout.addWidget(self.lbl_review_count)

        self.empty_review_label = QLabel(
            "今天暂无到期复习任务。\n你已经在进步了，继续保持。"
        )
        self.empty_review_label.setObjectName("reviewEmpty")
        self.empty_review_label.setAlignment(Qt.AlignCenter)
        self.empty_review_label.setWordWrap(True)
        self.empty_review_label.hide()
        layout.addWidget(self.empty_review_label)

        # 卡片列表容器：比传统表格更适合“快速扫一眼然后动手”的复习场景
        self.cards_container = QWidget()
        self.cards_container_layout = QVBoxLayout(self.cards_container)
        self.cards_container_layout.setSpacing(12)
        self.cards_container_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.cards_container, 1)

        # 当前选中的复习计划（用于底部按钮）
        self.selected_plan_id = None
        self.selected_plan_content = ""
        self.review_card_widgets = []

        self.btn_remember = QPushButton("记住了 · 进入下一阶段")
        self.btn_remember.setObjectName("btnSuccess")
        self.btn_remember.clicked.connect(lambda: self.judge_review(True))
        self.btn_remember.setEnabled(False)

        self.btn_forget = QPushButton("忘记了 · 重置进度")
        self.btn_forget.setObjectName("btnDanger")
        self.btn_forget.clicked.connect(lambda: self.judge_review(False))
        self.btn_forget.setEnabled(False)

        self.btn_remove = QPushButton("从记忆曲线移除（误加可删）")
        self.btn_remove.setObjectName("btnNeutral")
        self.btn_remove.clicked.connect(self.remove_from_curve)
        self.btn_remove.setEnabled(False)
        self._scalable_buttons.extend([self.btn_remember, self.btn_forget, self.btn_remove])

        judge_layout = QHBoxLayout()
        judge_layout.setSpacing(12)
        judge_layout.addWidget(self.btn_remember, 1)
        judge_layout.addWidget(self.btn_forget, 1)
        layout.addLayout(judge_layout)
        layout.addWidget(self.btn_remove)

        self.lbl_selected_hint = QLabel("请选择一条要复习的知识点")
        self.lbl_selected_hint.setObjectName("reviewHint")
        self.lbl_selected_hint.setAlignment(Qt.AlignCenter)
        self.lbl_selected_hint.setWordWrap(True)
        layout.addWidget(self.lbl_selected_hint)

        foot = QLabel("选中任意一张复习卡片，再点「记住 / 忘记」；误加条目用底部灰钮移除。")
        foot.setObjectName("reviewFoot")
        foot.setWordWrap(True)
        layout.addWidget(foot)

        scroll.setWidget(inner)
        outer.addWidget(scroll)

    def _clear_review_cards(self):
        """清空卡片列表，并重置选中状态。"""
        if hasattr(self, "cards_container_layout"):
            while self.cards_container_layout.count():
                item = self.cards_container_layout.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.deleteLater()
        self.review_card_widgets = []
        self.selected_plan_id = None
        self.selected_plan_content = ""
        if hasattr(self, "btn_remember"):
            self.btn_remember.setEnabled(False)
        if hasattr(self, "btn_forget"):
            self.btn_forget.setEnabled(False)
        if hasattr(self, "btn_remove"):
            self.btn_remove.setEnabled(False)
        if hasattr(self, "lbl_selected_hint"):
            self.lbl_selected_hint.setText("请选择一条要复习的知识点")

    def _select_review_card(self, plan_id: int, content: str):
        """卡片点击后：高亮选中并启用底部按钮。"""
        self.selected_plan_id = plan_id
        self.selected_plan_content = content or ""

        # 更新底部按钮状态
        if hasattr(self, "btn_remember"):
            self.btn_remember.setEnabled(True)
        if hasattr(self, "btn_forget"):
            self.btn_forget.setEnabled(True)
        if hasattr(self, "btn_remove"):
            self.btn_remove.setEnabled(True)

        if hasattr(self, "lbl_selected_hint"):
            self.lbl_selected_hint.setText(f"已选中：{self.selected_plan_content}")

        # 高亮卡片
        for w in getattr(self, "review_card_widgets", []):
            if w is None or not hasattr(w, "plan_id"):
                continue
            if w.plan_id == plan_id:
                w.setStyleSheet(QSS_REVIEW_CARD_SELECTED)
            else:
                w.setStyleSheet(QSS_REVIEW_CARD)

    # ================== 逻辑：新知识点如何进数据库 ==================
    def add_knowledge(self):
        """【艾宾浩斯算法 A面】新知识入库，计算 1 天后的首轮复习"""
        content = self.input_knowledge.text().strip()
        if not content:
            QMessageBox.warning(self, "提示", "知识点不能为空哦！")
            return

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        # 核心算法：第一轮复习通常定在 1 天后 [attachment_0](attachment)
        next_date = (datetime.datetime.now() + datetime.timedelta(days=REVIEW_INTERVALS[0])).strftime("%Y-%m-%d")

        # 1. 存入主任务表
        run_sql("INSERT INTO tasks (content, create_date) VALUES (?, ?)", (content, today))
        # 2. 获取刚才生成的 ID
        task_id = run_sql("SELECT id FROM tasks ORDER BY id DESC LIMIT 1")[0][0]
        # 3. 存入复习计划表 (stage 设为 0)
        run_sql("INSERT INTO review_plan (task_id, next_review_date, review_stage, mastery_level) VALUES (?, ?, ?, ?)",
                (task_id, next_date, 0, "新学习"))

        self.input_knowledge.clear()
        cn_today = fmt_cn_date(today)
        QMessageBox.information(
            self,
            "已加入",
            f"加入日期：{cn_today}\n"
            f"首次复习提醒日：{next_date}\n"
            f"（列表中「加入记忆曲线」列会显示该日期）",
        )
        self.refresh_review_table()

    # ================== 逻辑：大脑驱动（查询与评判） ==================
    def refresh_review_table(self):
        """【艾宾浩斯算法 B面】只显示今天或以前到期、且还没彻底掌握的任务"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        # 联表查询：从 review_plan 找日期，从 tasks 拿内容
        sql = """
            SELECT r.id, t.content, t.create_date, r.review_stage, r.next_review_date, r.mastery_level
            FROM review_plan r
            JOIN tasks t ON r.task_id = t.id
            WHERE r.next_review_date <= ?
            ORDER BY t.create_date DESC, r.id ASC
        """
        data = run_sql(sql, (today,))

        self.lbl_review_count.setText(f"到期：{len(data)} 条")

        # 刷新卡片列表
        self._clear_review_cards()

        is_empty = len(data) == 0
        self.empty_review_label.setVisible(is_empty)
        self.cards_container.setVisible(not is_empty)
        if is_empty:
            return

        for row_data in data:
            plan_id = row_data[0]
            content = row_data[1]
            create_date = row_data[2]
            stage_num = row_data[3]
            next_review_date = row_data[4]
            mastery_level = row_data[5] or ""

            card = ReviewCard(
                self,
                plan_id=plan_id,
                content=content,
                create_date=create_date,
                stage_num=stage_num,
                next_review_date=next_review_date,
                mastery_level=mastery_level,
            )
            self.cards_container_layout.addWidget(card)
            self.review_card_widgets.append(card)

    def judge_review(self, remembered):
        """【算法核心】根据复习反馈，决定该知识点是“晋级”还是“降级”"""
        if self.selected_plan_id is None:
            QMessageBox.warning(self, "提示", "请先选中一张复习卡片！")
            return

        plan_id = self.selected_plan_id
        res = run_sql("SELECT review_stage FROM review_plan WHERE id=?", (plan_id,))
        if not res:
            QMessageBox.warning(self, "提示", "该复习记录已不存在。")
            self.refresh_review_table()
            return
        current_stage = res[0][0]

        if remembered:
            # 1. 记住了：阶段加一
            next_stage = current_stage + 1
            # 如果超过了数组长度（30天），说明已经进入长期记忆
            if next_stage >= len(REVIEW_INTERVALS):
                QMessageBox.information(self, "通关", "该知识点已完全掌握，已从复习计划中移除。")
                run_sql("DELETE FROM review_plan WHERE id=?", (plan_id,))
                self.refresh_review_table()
                return
            level_text = "记得"
        else:
            # 2. 忘记了：打回第一阶段，从头开始
            next_stage = 0
            level_text = "忘记"

        # 根据新阶段从数组中取出要增加的天数
        days_to_add = REVIEW_INTERVALS[next_stage]
        next_date = (datetime.datetime.now() + datetime.timedelta(days=days_to_add)).strftime("%Y-%m-%d")

        # 更新数据库中的下一次复习时间和新阶段
        run_sql("UPDATE review_plan SET next_review_date=?, review_stage=?, mastery_level=? WHERE id=?",
                (next_date, next_stage, level_text, plan_id))

        QMessageBox.information(self, "已更新", f"下一次复习日期：{next_date}")
        self.refresh_review_table()

    def remove_from_curve(self):
        """误加入记忆曲线时，删除复习计划及对应任务。"""
        if self.selected_plan_id is None:
            QMessageBox.warning(self, "提示", "请先选中一张要移除的复习卡片！")
            return

        plan_id = self.selected_plan_id
        name = self.selected_plan_content or ""
        ret = QMessageBox.question(
            self,
            "确认移除",
            f"确定从记忆曲线中移除「{name}」吗？\n将同时删除该条复习计划。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return
        res = run_sql("SELECT task_id FROM review_plan WHERE id=?", (plan_id,))
        if not res:
            QMessageBox.warning(self, "提示", "未找到该复习记录，可能已被删除。")
            self.refresh_review_table()
            return
        task_id = res[0][0]
        run_sql("DELETE FROM review_plan WHERE id=?", (plan_id,))
        run_sql("DELETE FROM tasks WHERE id=?", (task_id,))
        self.refresh_review_table()


# ================== 程序入口：开启你的高效学习 ==================
if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei UI", 10))

    # 实例化并显示主窗体
    window = SuperStudyApp()
    window.show()

    # 进入程序主循环
    sys.exit(app.exec_())