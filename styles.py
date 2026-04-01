# -*- coding: utf-8 -*-
"""
Study+ 全局 QSS 样式库
包含所有界面的视觉定义，绝对保持原有的清新绿与大圆角设计。
"""
# styles.py

def build_tab_bar_qss(tab_font_pt=15):
    """
    动态生成选项卡样式
    :param tab_font_pt: 字体大小
    """
    return f"""
    QTabBar::tab {{
        min-height: 48px;
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

# -*- coding: utf-8 -*-
"""
Study+ 全局 QSS 样式库
包含所有界面的视觉定义，绝对保持原有的清新绿与大圆角设计。
"""

QSS_APP_GLOBAL = """
QWidget { font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC", sans-serif; color: #2d3d36; }
QMainWindow { background-color: #eef3f0; }
QTabWidget::pane { border: none; background: transparent; top: -1px; }
QTabBar::tab { min-height: 48px; min-width: 200px; padding: 12px 40px; font-size: 15px; font-weight: 600; color: #5a6962; background-color: #dfe9e3; border-top-left-radius: 20px; border-top-right-radius: 20px; margin-right: 6px; }
QTabBar::tab:selected { color: #2d5a4a; background-color: #ffffff; border-bottom: 3px solid #5b8a7a; }
QTabBar::tab:hover:!selected { background-color: #d2e2d8; }
QGroupBox { font-size: 15px; font-weight: 700; color: #1e2d28; border: 1px solid #d4e4da; border-radius: 22px; margin-top: 18px; padding: 22px 20px 20px 20px; background-color: #ffffff; }
QGroupBox::title { subcontrol-origin: margin; left: 18px; padding: 0 10px; }
QLabel { color: #3d4f47; }
QPushButton { background-color: #5b8a7a; color: #ffffff; border: none; border-radius: 18px; font-weight: 700; font-size: 15px; min-height: 48px; padding: 12px 22px; }
QPushButton:hover { background-color: #4d7a6b; }
QPushButton:pressed { background-color: #42695c; }
QPushButton:disabled { background-color: #d5ded8; color: #8a9a92; }
QLineEdit { min-height: 48px; padding: 12px 18px; border-radius: 18px; border: 1px solid #d4e4da; background-color: #ffffff; font-size: 15px; color: #1e2d28; selection-background-color: #c5ddd2; }
QLineEdit:focus { border: 2px solid #5b8a7a; }
QScrollArea { border: none; background: transparent; }
QTableWidget { background-color: #ffffff; alternate-background-color: #f4f9f6; color: #1e2d28; border: 1px solid #d4e4da; border-radius: 20px; gridline-color: #dce8e0; font-size: 14px; }
QTableWidget::item { padding: 12px 10px; min-height: 48px; }
QHeaderView::section { background-color: #eef6f1; color: #5a6962; font-weight: 700; font-size: 13px; padding: 14px 12px; border: none; border-bottom: 1px solid #d4e4da; }

/* 顶栏 */
QWidget#appHeader { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #e4f0ea); border-radius: 24px; border: 1px solid #d4e4da; }
QLabel#heroTitle { color: #1e2d28; font-size: 26px; font-weight: 800; letter-spacing: 0.3px; }
QLabel#heroSubtitle { color: #5a6962; font-size: 14px; font-weight: 500; line-height: 1.45; }
QLabel#headerTagPill { color: #3d5c50; font-size: 12px; font-weight: 600; padding: 10px 18px; background-color: #ddeee4; border-radius: 22px; border: 1px solid #c5ddd2; }

/* 按钮变体 */
QPushButton#btnPrimary { background-color: #e8f4ef; color: #2d5a4a; border: 1px solid #c5ddd2; border-radius: 18px; padding: 12px 22px; }
QPushButton#btnPrimary:hover { background-color: #d8ebe2; }
QPushButton#btnPrimary:pressed { background-color: #c5ddd2; }

/* 文件管理与笔记列表 */
QListWidget { background-color: #ffffff; border: 1px solid #d4e4da; border-radius: 20px; padding: 10px; color: #1e2d28; font-size: 14px; }
QListWidget::item { background-color: #f4f9f6; border-radius: 12px; margin-bottom: 8px; padding: 12px 15px; color: #2d3d36; }
QListWidget::item:hover { background-color: #d2e2d8; }
QListWidget::item:selected { background-color: #5b8a7a; color: #ffffff; }
QTextEdit { background-color: #ffffff; border: 1px solid #d4e4da; border-radius: 20px; padding: 15px; font-size: 14px; line-height: 1.6; color: #1e2d28; }
QTextEdit:focus { border: 2px solid #5b8a7a; }
"""

POMODORO_STYLE = """
QLabel#TimerDisplay { color: #2d5a4a; font-size: 120px; font-weight: bold; font-family: "Segoe UI", "微软雅黑"; margin: 20px; }
"""

DANGER_BUTTON = """
QPushButton { background-color: #e57373; color: white; border-radius: 18px; padding: 12px 22px; font-weight: bold; }
QPushButton:hover { background-color: #ef5350; }
QPushButton:pressed { background-color: #c62828; }
"""

MAIN_STYLE = QSS_APP_GLOBAL + POMODORO_STYLE

# 热力图专属样式
HEATMAP_STYLE = """
QWidget { background-color: #ffffff; border-radius: 30px; }
QLabel#HeaderTitle { color: #2e7d32; font-size: 60px; font-weight: bold; font-family: "Segoe UI", "Microsoft YaHei"; }
QFrame#StatsBox { background-color: #f1f8e9; border-radius: 20px; border: 2px solid #a5d6a7; padding: 30px 40px; }
QFrame[frameShape="VLine"] { color: #c8e6c9; }
QLabel#FooterLabel { color: #1b5e20; font-size: 32px; font-weight: bold; border-top: 2px solid #eee; padding-top: 15px; font-family: "微软雅黑"; }
"""