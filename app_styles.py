# -*- coding: utf-8 -*-
"""
Study+ 全局 QSS（清新绿 / 大圆角 / 呼吸感）
仅包含样式字符串，由界面代码通过 setStyleSheet 应用。
"""

# ---------------------------------------------------------------------------
# 主样式：窗口、标签页、表单控件、按钮变体、顶栏与通用标签层级
# ---------------------------------------------------------------------------
QSS_APP_GLOBAL = """
QWidget {
    font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC", sans-serif;
    color: #2d3d36;
}

QMainWindow {
    background-color: #eef3f0;
}

QTabWidget::pane {
    border: none;
    background: transparent;
    top: -1px;
}

QTabBar::tab {
    min-height: 48px;
    min-width: 200px;
    padding: 12px 40px;
    font-size: 15px;
    font-weight: 600;
    color: #5a6962;
    background-color: #dfe9e3;
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
    margin-right: 6px;
}

QTabBar::tab:selected {
    color: #2d5a4a;
    background-color: #ffffff;
    border-bottom: 3px solid #5b8a7a;
}

QTabBar::tab:hover:!selected {
    background-color: #d2e2d8;
}

QGroupBox {
    font-size: 15px;
    font-weight: 700;
    color: #1e2d28;
    border: 1px solid #d4e4da;
    border-radius: 22px;
    margin-top: 18px;
    padding: 22px 20px 20px 20px;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 18px;
    padding: 0 10px;
}

QLabel {
    color: #3d4f47;
}

QPushButton {
    background-color: #5b8a7a;
    color: #ffffff;
    border: none;
    border-radius: 18px;
    font-weight: 700;
    font-size: 15px;
    min-height: 48px;
    padding: 12px 22px;
}

QPushButton:hover {
    background-color: #4d7a6b;
}

QPushButton:pressed {
    background-color: #42695c;
}

QPushButton:disabled {
    background-color: #d5ded8;
    color: #8a9a92;
}

QLineEdit {
    min-height: 48px;
    padding: 12px 18px;
    border-radius: 18px;
    border: 1px solid #d4e4da;
    background-color: #ffffff;
    font-size: 15px;
    color: #1e2d28;
    selection-background-color: #c5ddd2;
}

QLineEdit:focus {
    border: 2px solid #5b8a7a;
}

QScrollArea {
    border: none;
    background: transparent;
}

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f4f9f6;
    color: #1e2d28;
    border: 1px solid #d4e4da;
    border-radius: 20px;
    gridline-color: #dce8e0;
    font-size: 14px;
}

QTableWidget::item {
    padding: 12px 10px;
    min-height: 48px;
}

QHeaderView::section {
    background-color: #eef6f1;
    color: #5a6962;
    font-weight: 700;
    font-size: 13px;
    padding: 14px 12px;
    border: none;
    border-bottom: 1px solid #d4e4da;
}

/* 顶栏 */
QWidget#appHeader {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #ffffff,
        stop:1 #e4f0ea);
    border-radius: 24px;
    border: 1px solid #d4e4da;
}

QLabel#heroTitle {
    color: #1e2d28;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: 0.3px;
}

QLabel#heroSubtitle {
    color: #5a6962;
    font-size: 14px;
    font-weight: 500;
    line-height: 1.45;
}

QLabel#sectionKicker {
    color: #4a7c6b;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.2px;
}

QLabel#headerTagPill {
    color: #3d5c50;
    font-size: 12px;
    font-weight: 600;
    padding: 10px 18px;
    background-color: #ddeee4;
    border-radius: 22px;
    border: 1px solid #c5ddd2;
}

/* 番茄钟 */
QLabel#pomoBody {
    color: #5a6962;
    font-size: 14px;
    font-weight: 500;
    line-height: 1.55;
    padding: 4px 2px;
}

QLabel#pomoToday {
    color: #5a6962;
    font-size: 13px;
    font-weight: 500;
    padding: 4px 2px 8px 2px;
}

QLabel#lblPomoTime {
    color: #1e2d28;
}

QWidget#pomoTimerCard {
    background-color: #ffffff;
    border: 1px solid #d4e4da;
    border-radius: 24px;
}

QLabel#pomoTip {
    color: #7a8f86;
    font-size: 12px;
    font-weight: 500;
    padding: 8px 6px 4px 6px;
}

QLabel#pomoStatus {
    color: #7a8f86;
    font-size: 13px;
    font-weight: 500;
    padding: 14px 12px 6px 12px;
}

/* 智能复习 */
QLabel#reviewBanner {
    color: #2d5a4a;
    font-size: 13px;
    font-weight: 600;
    line-height: 1.5;
    padding: 14px 18px;
    background-color: #e4f2eb;
    border-radius: 20px;
    border: 1px solid #c5ddd2;
}

QLabel#reviewListTitle {
    color: #1e2d28;
    font-size: 17px;
    font-weight: 800;
    padding: 6px 2px 2px 2px;
}

QLabel#reviewCount {
    color: #5a6962;
    font-size: 13px;
    font-weight: 500;
    padding: 2px 2px 8px 2px;
}

QLabel#reviewEmpty {
    color: #5a6962;
    font-size: 14px;
    font-weight: 500;
    line-height: 1.55;
    padding: 22px 20px;
    background-color: #f4f9f6;
    border: 1px solid #dce8e0;
    border-radius: 22px;
}

QLabel#reviewHint {
    color: #7a8f86;
    font-size: 12px;
    font-weight: 500;
    padding: 8px 8px 4px 8px;
}

QLabel#reviewFoot {
    color: #8a9a92;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 6px 8px 6px;
}

/* 复习卡片内文字层级 */
QLabel#reviewCardTitle {
    color: #1e2d28;
    font-size: 17px;
    font-weight: 800;
    padding: 2px 0;
}

QLabel#reviewCardMeta {
    color: #5a6962;
    font-size: 13px;
    font-weight: 500;
    padding: 2px 0;
}

QLabel#reviewCardNext {
    color: #3d6b5c;
    font-size: 13px;
    font-weight: 700;
    padding: 4px 0 2px 0;
}

/* 按钮变体 */
QPushButton#btnSuccess {
    background-color: #5a9179;
    border-radius: 18px;
}

QPushButton#btnSuccess:hover {
    background-color: #4d806a;
}

QPushButton#btnDanger {
    background-color: #c9a09a;
    border-radius: 18px;
}

QPushButton#btnDanger:hover {
    background-color: #b8908a;
}

QPushButton#btnNeutral {
    background-color: #8a9f96;
    border-radius: 18px;
}

QPushButton#btnNeutral:hover {
    background-color: #7a8f86;
}

QPushButton#btnPrimary {
    background-color: #e8f4ef;
    color: #2d5a4a;
    border: 1px solid #c5ddd2;
    border-radius: 18px;
    padding: 12px 22px;
}

QPushButton#btnPrimary:hover {
    background-color: #d8ebe2;
}

QPushButton#btnPrimary:pressed {
    background-color: #c5ddd2;
}

QPushButton#btnReset {
    background-color: #f7eceb;
    color: #8b534c;
    border: 1px solid #e8d4d2;
    border-radius: 18px;
    padding: 12px 22px;
}

QPushButton#btnReset:hover {
    background-color: #f0e0de;
}

QPushButton#btnReset:pressed {
    background-color: #e8d4d2;
}

/* ===========================================================================
   新增：文件管理与笔记页特定样式 (对齐清新绿主题)
   =========================================================================== */

/* 文件管理页大标题 - 对齐 heroTitle 风格 */
QLabel#organizerTitle {
    color: #1e2d28;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: 0.3px;
    padding: 10px 0;
}

/* 通用列表控件 (用于日志展示和笔记列表) */
QListWidget {
    background-color: #ffffff;
    border: 1px solid #d4e4da;
    border-radius: 20px;
    padding: 10px;
    color: #1e2d28;
    font-size: 14px;
}

QListWidget::item {
    background-color: #f4f9f6;
    border-radius: 12px;
    margin-bottom: 8px;
    padding: 12px 15px;
    color: #2d3d36;
}

QListWidget::item:hover {
    background-color: #d2e2d8;
}

QListWidget::item:selected {
    background-color: #5b8a7a;
    color: #ffffff;
}

/* 笔记编辑区域 */
QTextEdit#noteEditor {
    background-color: #ffffff;
    border: 1px solid #d4e4da;
    border-radius: 20px;
    padding: 15px;
    font-size: 14px;
    line-height: 1.6;
    color: #1e2d28;
}

QTextEdit#noteEditor:focus {
    border: 2px solid #5b8a7a;
}

"""

# ---------------------------------------------------------------------------
# 复习卡片：默认 / 选中（整块卡片 setStyleSheet）
# ---------------------------------------------------------------------------
QSS_REVIEW_CARD = """
QWidget#reviewCard {
    background-color: #ffffff;
    border: 1px solid #d4e4da;
    border-radius: 22px;
}
"""

QSS_REVIEW_CARD_SELECTED = """
QWidget#reviewCard {
    background-color: #f2faf6;
    border: 2px solid #5b8a7a;
    border-radius: 22px;
}
"""
# --- 在这里插入 DANGER_BUTTON ---
DANGER_BUTTON = """
QPushButton {
    background-color: #e57373; 
    color: white;
    border-radius: 10px;
    padding: 8px 15px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #ef5350;
}
QPushButton:pressed {
    background-color: #c62828;
}
"""

def build_tab_bar_qss(tab_height_px: int, tab_font_pt: int) -> str:
    """随窗口缩放的标签栏样式（仍保持清新绿主题）。"""
    return f"""
    QTabBar::tab {{
        min-height: {tab_height_px}px;
        min-width: 200px;
        padding: 12px 40px;
        font-size: {tab_font_pt}px;
        font-weight: 600;
        color: #5a6962;
        background-color: #dfe9e3;
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
        margin-right: 6px;
    }}
    QTabBar::tab:selected {{
        color: #2d5a4a;
        background-color: #ffffff;
        border-bottom: 3px solid #5b8a7a;
    }}
    QTabBar::tab:hover:!selected {{
        background-color: #d2e2d8;
    }}
    """

# ==========================================================
# 第二部分：新增的番茄钟高级感样式
# ==========================================================
POMODORO_STYLE = """
/* 右侧番茄钟悬浮卡片 */
QFrame#PomodoroCard {
    background-color: #ffffff;
    border-radius: 30px;
    border: 1px solid #f0f0f0;
}

/* 时间大数字 - 现代感 */
QLabel#TimerDisplay {
    color: #333333;
    font-size: 90px;
    font-weight: bold;
    font-family: "Segoe UI", "微软雅黑";
}

/* 开始按钮 - 莫兰迪绿 */
QPushButton#StartFocusBtn {
    background-color: #A5D6A7;
    color: white;
    border-radius: 22px;
    font-size: 20px;
    font-weight: bold;
    padding: 12px 40px;
}
QPushButton#StartFocusBtn:hover {
    background-color: #81C784;
}

/* 左侧标题 */
QLabel#BigTitle {
    font-size: 32px;
    font-weight: bold;
    color: #333;
}
"""


# ==========================================================
# 第三部分：最终合并 (这是 main.py 会调用的变量)
# ==========================================================
# 我们用 + 号把所有样式连起来
MAIN_STYLE = QSS_APP_GLOBAL + POMODORO_STYLE