import sys
import sqlite3
import datetime
import os
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ==============================================================================
# 傻瓜式操作第一步：导入环境修复代码 (必须在最前面)
# ==============================================================================
dirname = os.path.dirname(PyQt5.__file__)
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(dirname, 'Qt5', 'plugins', 'platforms')

# ==============================================================================
# 傻瓜式操作第二步：QSS 高级样式定义 (整容核心)
# ==============================================================================
QSS_STYLESHEET = """
VictoryHeatmapPlugin {
    background-color: #ffffff; /* 清新绿配色：纯白背景 */
    border-radius: 30px;      /* 所有的窗口、按钮和容器必须使用大圆角 */
}

/* 顶部标题区 */
QLabel#HeaderTitle {
    color: #2e7d32;            /* 深绿色 */
    font-size: 60px;
    font-weight: bold;
    font-family: "Segoe UI", "Microsoft YaHei"; /* 现代无衬线字体 */
}

/* 数据统计卡片 (年、月、周) */
QFrame#StatsBox {
    background-color: #f1f8e9; /* 清新绿风格：淡绿背景 */
    border-radius: 20px;       /* 圆角协调一些 */
    border: 2px solid #a5d6a7;  /* 柔和边框 */
    padding: 30px 40px;        /* 增加 Padding (内边距) */
}

QLabel#StatTitle {
    color: #666666;             /* 灰色 */
    font-size: 28px;
    font-family: "Segoe UI", "Microsoft YaHei";
    font-weight: bold;
}

QLabel#StatValue {
    color: #1b5e20;             /* 深绿 */
    font-size: 48px;
    font-weight: bold;
    font-family: "Segoe UI";
}

/* 分隔线样式 */
QFrame[frameShape="VLine"] {
    color: #c8e6c9;
}

/* 底部总计 */
QLabel#FooterLabel {
    color: #1b5e20;
    font-size: 32px;
    font-weight: bold;
    border-top: 2px solid #eee;
    padding-top: 15px;
    font-family: "微软雅黑";
}
"""

# ==============================================================================
# 傻瓜式操作第三步：基础格子 Item 类 (处理颜色和文字)
# ==============================================================================
COLOR_LEVELS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

class HeatmapItem(QGraphicsRectItem):
    """适配 30 天显示的精致格子"""
    def __init__(self, x, y, size, minutes, date_str, low_bar=10, parent=None):
        super().__init__(x, y, size, size, parent)
        self.minutes = minutes
        self.date_str = date_str
        self.low_bar = low_bar # 低保设置 (核心驱动力)
        
        # 根据分钟数 and 低保设置，决定颜色梯度
        color_hex = self.get_color_by_minutes(minutes)
        self.setBrush(QBrush(QColor(color_hex)))
        
        # penStyle报错修复
        self.setPen(QPen(Qt.NoPen))
        
        # 增加 hover 事件
        self.setAcceptHoverEvents(True)
        self.setToolTip(f"{date_str}\n专注: {minutes} 分钟")

    def get_color_by_minutes(self, mins):
        if mins == 0: return COLOR_LEVELS[0]
        # 核心逻辑：完成低保亮绿格
        if mins < self.low_bar: return COLOR_LEVELS[1] # 浅绿
        if mins <= 30: return COLOR_LEVELS[1]
        if mins <= 60: return COLOR_LEVELS[2]
        if mins <= 120: return COLOR_LEVELS[3]
        return COLOR_LEVELS[4] # 深绿

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.minutes >= 0:
            # 细节全栈：深绿格用白字，浅绿格用灰字
            text_color = Qt.white if self.minutes > 60 else QColor("#666666")
            painter.setPen(QPen(text_color))
            
            # 缩小数字字体
            painter.setFont(QFont("Segoe UI", 18, QFont.Bold))
            display_text = str(int(self.minutes)) if self.minutes > 0 else ""
            painter.drawText(self.rect(), Qt.AlignCenter, display_text)
            
            # 左上角微缩日期
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(self.rect().adjusted(6, 4, -5, -5), Qt.AlignTop | Qt.AlignLeft, self.date_str[5:])

# ==============================================================================
# 傻瓜式操作第三步：基础格子 Item 类 (处理颜色和文字)
# ==============================================================================
COLOR_LEVELS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

class HeatmapItem(QGraphicsRectItem):
    """适配 30 天显示的精致格子"""
    def __init__(self, x, y, size, minutes, date_str, low_bar=10, parent=None):
        super().__init__(x, y, size, size, parent)
        self.minutes = minutes
        self.date_str = date_str
        self.low_bar = low_bar # 低保设置 (核心驱动力)
        
        # 根据分钟数 and 低保设置，决定颜色梯度
        color_hex = self.get_color_by_minutes(minutes)
        self.setBrush(QBrush(QColor(color_hex)))
        
        # penStyle报错修复
        self.setPen(QPen(Qt.NoPen))
        
        # 增加 hover 事件
        self.setAcceptHoverEvents(True)
        self.setToolTip(f"{date_str}\n专注: {minutes} 分钟")

    def get_color_by_minutes(self, mins):
        if mins == 0: return COLOR_LEVELS[0]
        # 核心逻辑：完成低保亮绿格
        if mins < self.low_bar: return COLOR_LEVELS[1] # 浅绿
        if mins <= 30: return COLOR_LEVELS[1]
        if mins <= 60: return COLOR_LEVELS[2]
        if mins <= 120: return COLOR_LEVELS[3]
        return COLOR_LEVELS[4] # 深绿

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.minutes >= 0:
            # 细节全栈：深绿格用白字，浅绿格用灰字
            text_color = Qt.white if self.minutes > 60 else QColor("#666666")
            painter.setPen(QPen(text_color))
            
            # 缩小数字字体
            painter.setFont(QFont("Segoe UI", 18, QFont.Bold))
            display_text = str(int(self.minutes)) if self.minutes > 0 else ""
            painter.drawText(self.rect(), Qt.AlignCenter, display_text)
            
            # 左上角微缩日期
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(self.rect().adjusted(6, 4, -5, -5), Qt.AlignTop | Qt.AlignLeft, self.date_str[5:])

# ==============================================================================
# 傻瓜式操作第四步：视图 View 类 (处理 30 天格子排列)
# ==============================================================================
class HeatmapView(QGraphicsView):
    def __init__(self, data_map, low_bar=10):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        
        # 样式整洁
        self.setStyleSheet("border: none; background: transparent;")
        
        # 禁用滚动条，确保一屏全显
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 针对 30 天显示的黄金尺寸：一行 5 个，共 6 行
        self.item_size = 95  
        self.spacing = 15     
        self.render_heatmap(data_map, low_bar)

    def render_heatmap(self, data_map, low_bar):
        dates = sorted(data_map.keys())
        if not dates: return
        for i, date_str in enumerate(dates):
            # 一行显示 5 个，30 天正好全显
            row, col = i // 5, i % 5  # cc240801-b2bd-419b-a010-09a15a86a605
            mins = data_map.get(date_str, 0)
            item = HeatmapItem(col * (self.item_size + self.spacing), 
                               row * (self.item_size + self.spacing), 
                               self.item_size, mins, date_str, low_bar)
            self.scene.addItem(item)

# ==============================================================================
# 傻瓜式操作第五步：主插件窗口 (统管全局)
# ==============================================================================
class VictoryHeatmapPlugin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏆 我的成就看板")
        
        # 窗口设为屏幕宽度的 55%，高度的 90%，确保格子完全装进
        screen = QApplication.primaryScreen().geometry()
        self.resize(int(screen.width() * 0.55), int(screen.height() * 0.9))
        
        # 统一应用整容级 QSS 样式表
        self.setStyleSheet(QSS_STYLESHEET)
        
        # 实时数据获取
        self.data_map = self.get_heatmap_data(days=30)
        self.stats = self.get_advanced_stats()
        
        self.init_ui()

    def get_heatmap_data(self, days=30):
        try:
            conn = sqlite3.connect("super_study.db")
            data = {}
            # 循环天数从今天开始向前推 days 天
            for i in range(days):
                date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                res = conn.execute("SELECT SUM(focus_minutes) FROM pomodoro_logs WHERE focus_date = ?", (date,)).fetchone()[0]
                data[date] = res if res else 0
            conn.close()
            # 确保字典排序（从左往右流逝）
            return dict(sorted(data.items()))
        except Exception as e:
            # 无数据库时的模拟数据，防止崩溃
            return {}

    def get_advanced_stats(self):
        """精准计算年、月、周的逻辑"""
        now = datetime.datetime.now()
        stats = {"year": 0, "month": 0, "week": 0, "week_num": now.isocalendar()[1]} # 标注第几周
        try:
            conn = sqlite3.connect("super_study.db")
            # 本年统计
            stats['year'] = conn.execute("SELECT SUM(focus_minutes) FROM pomodoro_logs WHERE strftime('%Y', focus_date) = ?", (now.strftime('%Y'),)).fetchone()[0] or 0
            # 本月统计
            stats['month'] = conn.execute("SELECT SUM(focus_minutes) FROM pomodoro_logs WHERE strftime('%Y-%m', focus_date) = ?", (now.strftime('%Y-%m'),)).fetchone()[0] or 0
            # 本周统计 (ISO周)
            stats['week'] = conn.execute("SELECT SUM(focus_minutes) FROM pomodoro_logs WHERE strftime('%W', focus_date) = ?", (now.strftime('%W'),)).fetchone()[0] or 0
            conn.close()
        except Exception as e:
            # 无数据库时的模拟数据，防止崩溃
            stats['year'], stats['month'], stats['week'] = 25, 25, 25
            
        return stats

    def init_ui(self):
        layout = QVBoxLayout(self)
        # 增加 Padding (内边距) 让布局有呼吸感
        layout.setContentsMargins(60, 40, 60, 40)

        # 1. 顶部区域：绿色叶子 + Focus Heatmap
        header = QHBoxLayout()
        # 增加 Emoji 🌿
        header.addWidget(QLabel("🌿", font=QFont("Segoe UI Emoji", 70)))
        
        title_label = QLabel("Focus Heatmap")
        title_label.setObjectName("HeaderTitle") # 对应 QSS #HeaderTitle
        title_label.setFont(QFont("Avenir Next", 60, QFont.Bold)) # 60px加粗
        title_label.setStyleSheet("color: #2e7d32;") # 深绿
        
        header.addWidget(title_label)
        header.addStretch() # 将标题推向最左侧
        
        # --- 核心修正点：直接把 header 加入 layout，不要经过中间变量 ---
        layout.addLayout(header) 
        
        layout.addSpacing(20) # 顶部留白

        # 2. 中间区域：30 天格子区域 (居中平铺)
        self.view = HeatmapView(self.data_map)
        layout.addWidget(self.view, alignment=Qt.AlignCenter)
        
        # 强力撑开上方空间
        layout.addStretch(1) # f39665c3-b413-40fa-ba4b-97e38258e705

        # 3. 数据统计卡片区域 (年、月、周)
        stats_box = QFrame()
        stats_box.setObjectName("StatsBox") # 对应 QSS #StatsBox
        s_layout = QHBoxLayout(stats_box) # 改为横向布局
        s_layout.setContentsMargins(40, 30, 40, 30) # 增大卡片内部边距
        s_layout.setSpacing(20) # Spacing 加大
        
        # 定义一个通用的“统计格子”工厂函数
        def add_box(t, v):
            w = QVBoxLayout()
            l1 = QLabel(t); l1.setStyleSheet("color: #666; font-size: 28px;"); l1.setFont(QFont("微软雅黑", 28, QFont.Bold))
            l1.setAlignment(Qt.AlignCenter)

            l2 = QLabel(f"{v} min"); l2.setStyleSheet("color: #1b5e20; font-size: 48px; font-weight: bold;"); l2.setFont(QFont("Segoe UI", 48, QFont.Bold))
            l2.setAlignment(Qt.AlignCenter)
            
            w.addWidget(l1)
            w.addWidget(l2)
            s_layout.addLayout(w)
            
            line = QFrame()
            line.setFrameShape(QFrame.VLine)
            line.setFrameShadow(QFrame.Sunken)
            line.setStyleSheet("color: #c8e6c9;")
            s_layout.addWidget(line)
        
        add_box(f"{datetime.datetime.now().year}年累计", self.stats['year'])
        add_box(f"{datetime.datetime.now().month}月专注", self.stats['month'])
        
        # 移除最后一个分隔线
        if s_layout.count() > 0:
            s_layout.itemAt(s_layout.count()-1).widget().deleteLater() 
            
        add_box(f"第 {self.stats['week_num']} 周", self.stats['week']) 
        
        if s_layout.count() > 0:
            s_layout.itemAt(s_layout.count()-1).widget().deleteLater()

        layout.addSpacing(30)
        layout.addWidget(stats_box)
        layout.addStretch(1)

        # 4. 置底总计文字
        total_all = sum(self.data_map.values())
        footer = QLabel(f"成就达成：{total_all} 分钟")
        footer.setObjectName("FooterLabel")
        footer.setFont(QFont("微软雅黑", 32, QFont.Bold))
        footer.setStyleSheet("color: #1b5e20; border-top: 2px solid #eee; padding-top: 15px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

# ==============================================================================
# 启动代码块
# ==============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VictoryHeatmapPlugin()
    window.show()
    sys.exit(app.exec_())

import sys
import sqlite3
import datetime
import os
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ==============================================================================
# 傻瓜式操作第一步：导入环境修复代码 (必须在最前面)
# ==============================================================================
dirname = os.path.dirname(PyQt5.__file__)
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(dirname, 'Qt5', 'plugins', 'platforms')

# ==============================================================================
# 傻瓜式操作第二步：QSS 高级样式定义 (整容核心)
# ==============================================================================
QSS_STYLESHEET = """
VictoryHeatmapPlugin {
    background-color: #ffffff; /* 清新绿配色：纯白背景 */
    border-radius: 30px;      /* 所有的窗口、按钮和容器必须使用大圆角 */
}

/* 顶部标题区 */
QLabel#HeaderTitle {
    color: #2e7d32;            /* 深绿色 */
    font-size: 60px;
    font-weight: bold;
    font-family: "Segoe UI", "Microsoft YaHei"; /* 现代无衬线字体 */
}

/* 数据统计卡片 (年、月、周) */
QFrame#StatsBox {
    background-color: #f1f8e9; /* 清新绿风格：淡绿背景 */
    border-radius: 20px;       /* 圆角协调一些 */
    border: 2px solid #a5d6a7;  /* 柔和边框 */
    padding: 30px 40px;        /* 增加 Padding (内边距) */
}

QLabel#StatTitle {
    color: #666666;             /* 灰色 */
    font-size: 28px;
    font-family: "Segoe UI", "Microsoft YaHei";
    font-weight: bold;
}

QLabel#StatValue {
    color: #1b5e20;             /* 深绿 */
    font-size: 48px;
    font-weight: bold;
    font-family: "Segoe UI";
}

/* 分隔线样式 */
QFrame[frameShape="VLine"] {
    color: #c8e6c9;
}

/* 底部总计 */
QLabel#FooterLabel {
    color: #1b5e20;
    font-size: 32px;
    font-weight: bold;
    border-top: 2px solid #eee;
    padding-top: 15px;
    font-family: "微软雅黑";
}
"""

# ==============================================================================
# 傻瓜式操作第三步：基础格子 Item 类 (处理颜色和文字)
# ==============================================================================
COLOR_LEVELS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

class HeatmapItem(QGraphicsRectItem):
    """适配 30 天显示的精致格子"""
    def __init__(self, x, y, size, minutes, date_str, low_bar=10, parent=None):
        super().__init__(x, y, size, size, parent)
        self.minutes = minutes
        self.date_str = date_str
        self.low_bar = low_bar # 低保设置 (核心驱动力)
        
        # 根据分钟数 and 低保设置，决定颜色梯度
        color_hex = self.get_color_by_minutes(minutes)
        self.setBrush(QBrush(QColor(color_hex)))
        
        # penStyle报错修复
        self.setPen(QPen(Qt.NoPen))
        
        # 增加 hover 事件
        self.setAcceptHoverEvents(True)
        self.setToolTip(f"{date_str}\n专注: {minutes} 分钟")

    def get_color_by_minutes(self, mins):
        if mins == 0: return COLOR_LEVELS[0]
        # 核心逻辑：完成低保亮绿格
        if mins < self.low_bar: return COLOR_LEVELS[1] # 浅绿
        if mins <= 30: return COLOR_LEVELS[1]
        if mins <= 60: return COLOR_LEVELS[2]
        if mins <= 120: return COLOR_LEVELS[3]
        return COLOR_LEVELS[4] # 深绿

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.minutes >= 0:
            # 细节全栈：深绿格用白字，浅绿格用灰字
            text_color = Qt.white if self.minutes > 60 else QColor("#666666")
            painter.setPen(QPen(text_color))
            
            # 缩小数字字体
            painter.setFont(QFont("Segoe UI", 18, QFont.Bold))
            display_text = str(int(self.minutes)) if self.minutes > 0 else ""
            painter.drawText(self.rect(), Qt.AlignCenter, display_text)
            
            # 左上角微缩日期
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(self.rect().adjusted(6, 4, -5, -5), Qt.AlignTop | Qt.AlignLeft, self.date_str[5:])

# ==============================================================================
# 傻瓜式操作第三步：基础格子 Item 类 (处理颜色和文字)
# ==============================================================================
COLOR_LEVELS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

class HeatmapItem(QGraphicsRectItem):
    """适配 30 天显示的精致格子"""
    def __init__(self, x, y, size, minutes, date_str, low_bar=10, parent=None):
        super().__init__(x, y, size, size, parent)
        self.minutes = minutes
        self.date_str = date_str
        self.low_bar = low_bar # 低保设置 (核心驱动力)
        
        # 根据分钟数 and 低保设置，决定颜色梯度
        color_hex = self.get_color_by_minutes(minutes)
        self.setBrush(QBrush(QColor(color_hex)))
        
        # penStyle报错修复
        self.setPen(QPen(Qt.NoPen))
        
        # 增加 hover 事件
        self.setAcceptHoverEvents(True)
        self.setToolTip(f"{date_str}\n专注: {minutes} 分钟")

    def get_color_by_minutes(self, mins):
        if mins == 0: return COLOR_LEVELS[0]
        # 核心逻辑：完成低保亮绿格
        if mins < self.low_bar: return COLOR_LEVELS[1] # 浅绿
        if mins <= 30: return COLOR_LEVELS[1]
        if mins <= 60: return COLOR_LEVELS[2]
        if mins <= 120: return COLOR_LEVELS[3]
        return COLOR_LEVELS[4] # 深绿

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.minutes >= 0:
            # 细节全栈：深绿格用白字，浅绿格用灰字
            text_color = Qt.white if self.minutes > 60 else QColor("#666666")
            painter.setPen(QPen(text_color))
            
            # 缩小数字字体
            painter.setFont(QFont("Segoe UI", 18, QFont.Bold))
            display_text = str(int(self.minutes)) if self.minutes > 0 else ""
            painter.drawText(self.rect(), Qt.AlignCenter, display_text)
            
            # 左上角微缩日期
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(self.rect().adjusted(6, 4, -5, -5), Qt.AlignTop | Qt.AlignLeft, self.date_str[5:])

# ==============================================================================
# 傻瓜式操作第四步：视图 View 类 (处理 30 天格子排列)
# ==============================================================================
class HeatmapView(QGraphicsView):
    def __init__(self, data_map, low_bar=10):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        
        # 样式整洁
        self.setStyleSheet("border: none; background: transparent;")
        
        # 禁用滚动条，确保一屏全显
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 针对 30 天显示的黄金尺寸：一行 5 个，共 6 行
        self.item_size = 95  
        self.spacing = 15     
        self.render_heatmap(data_map, low_bar)

    def render_heatmap(self, data_map, low_bar):
        dates = sorted(data_map.keys())
        if not dates: return
        for i, date_str in enumerate(dates):
            # 一行显示 5 个，30 天正好全显
            row, col = i // 5, i % 5  # cc240801-b2bd-419b-a010-09a15a86a605
            mins = data_map.get(date_str, 0)
            item = HeatmapItem(col * (self.item_size + self.spacing), 
                               row * (self.item_size + self.spacing), 
                               self.item_size, mins, date_str, low_bar)
            self.scene.addItem(item)

# ==============================================================================
# 傻瓜式操作第五步：主插件窗口 (统管全局)
# ==============================================================================
class VictoryHeatmapPlugin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏆 我的成就看板")
        
        # 窗口设为屏幕宽度的 55%，高度的 90%，确保格子完全装进
        screen = QApplication.primaryScreen().geometry()
        self.resize(int(screen.width() * 0.55), int(screen.height() * 0.9))
        
        # 统一应用整容级 QSS 样式表
        self.setStyleSheet(QSS_STYLESHEET)
        
        # 实时数据获取
        self.data_map = self.get_heatmap_data(days=30)
        self.stats = self.get_advanced_stats()
        
        self.init_ui()

    def get_heatmap_data(self, days=30):
        try:
            conn = sqlite3.connect("super_study.db")
            data = {}
            # 循环天数从今天开始向前推 days 天
            for i in range(days):
                date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                res = conn.execute("SELECT SUM(focus_minutes) FROM pomodoro_logs WHERE focus_date = ?", (date,)).fetchone()[0]
                data[date] = res if res else 0
            conn.close()
            # 确保字典排序（从左往右流逝）
            return dict(sorted(data.items()))
        except Exception as e:
            # 无数据库时的模拟数据，防止崩溃
            return {}

    def get_advanced_stats(self):
        """精准计算年、月、周的逻辑"""
        now = datetime.datetime.now()
        stats = {"year": 0, "month": 0, "week": 0, "week_num": now.isocalendar()[1]} # 标注第几周
        try:
            conn = sqlite3.connect("super_study.db")
            # 本年统计
            stats['year'] = conn.execute("SELECT SUM(focus_minutes) FROM pomodoro_logs WHERE strftime('%Y', focus_date) = ?", (now.strftime('%Y'),)).fetchone()[0] or 0
            # 本月统计
            stats['month'] = conn.execute("SELECT SUM(focus_minutes) FROM pomodoro_logs WHERE strftime('%Y-%m', focus_date) = ?", (now.strftime('%Y-%m'),)).fetchone()[0] or 0
            # 本周统计 (ISO周)
            stats['week'] = conn.execute("SELECT SUM(focus_minutes) FROM pomodoro_logs WHERE strftime('%W', focus_date) = ?", (now.strftime('%W'),)).fetchone()[0] or 0
            conn.close()
        except Exception as e:
            # 无数据库时的模拟数据，防止崩溃
            stats['year'], stats['month'], stats['week'] = 25, 25, 25
            
        return stats

    def init_ui(self):
        layout = QVBoxLayout(self)
        # 增加 Padding (内边距) 让布局有呼吸感
        layout.setContentsMargins(60, 40, 60, 40)

        # 1. 顶部区域：绿色叶子 + Focus Heatmap
        header = QHBoxLayout()
        # 增加 Emoji 🌿
        header.addWidget(QLabel("🌿", font=QFont("Segoe UI Emoji", 70)))
        
        title_label = QLabel("Focus Heatmap")
        title_label.setObjectName("HeaderTitle") # 对应 QSS #HeaderTitle
        title_label.setFont(QFont("Avenir Next", 60, QFont.Bold)) # 60px加粗
        title_label.setStyleSheet("color: #2e7d32;") # 深绿
        
        header.addWidget(title_label)
        header.addStretch() # 将标题推向最左侧
        
        # --- 核心修正点：直接把 header 加入 layout，不要经过中间变量 ---
        layout.addLayout(header) 
        
        layout.addSpacing(20) # 顶部留白

        # 2. 中间区域：30 天格子区域 (居中平铺)
        self.view = HeatmapView(self.data_map)
        layout.addWidget(self.view, alignment=Qt.AlignCenter)
        
        # 强力撑开上方空间
        layout.addStretch(1) # f39665c3-b413-40fa-ba4b-97e38258e705

        # 3. 数据统计卡片区域 (年、月、周)
        stats_box = QFrame()
        stats_box.setObjectName("StatsBox") # 对应 QSS #StatsBox
        s_layout = QHBoxLayout(stats_box) # 改为横向布局
        s_layout.setContentsMargins(40, 30, 40, 30) # 增大卡片内部边距
        s_layout.setSpacing(20) # Spacing 加大
        
        # 定义一个通用的“统计格子”工厂函数
        def add_box(t, v):
            w = QVBoxLayout()
            l1 = QLabel(t); l1.setStyleSheet("color: #666; font-size: 28px;"); l1.setFont(QFont("微软雅黑", 28, QFont.Bold))
            l1.setAlignment(Qt.AlignCenter)

            l2 = QLabel(f"{v} min"); l2.setStyleSheet("color: #1b5e20; font-size: 48px; font-weight: bold;"); l2.setFont(QFont("Segoe UI", 48, QFont.Bold))
            l2.setAlignment(Qt.AlignCenter)
            
            w.addWidget(l1)
            w.addWidget(l2)
            s_layout.addLayout(w)
            
            line = QFrame()
            line.setFrameShape(QFrame.VLine)
            line.setFrameShadow(QFrame.Sunken)
            line.setStyleSheet("color: #c8e6c9;")
            s_layout.addWidget(line)
        
        add_box(f"{datetime.datetime.now().year}年累计", self.stats['year'])
        add_box(f"{datetime.datetime.now().month}月专注", self.stats['month'])
        
        # 移除最后一个分隔线
        if s_layout.count() > 0:
            s_layout.itemAt(s_layout.count()-1).widget().deleteLater() 
            
        add_box(f"第 {self.stats['week_num']} 周", self.stats['week']) 
        
        if s_layout.count() > 0:
            s_layout.itemAt(s_layout.count()-1).widget().deleteLater()

        layout.addSpacing(30)
        layout.addWidget(stats_box)
        layout.addStretch(1)

        # 4. 置底总计文字
        total_all = sum(self.data_map.values())
        footer = QLabel(f"成就达成：{total_all} 分钟")
        footer.setObjectName("FooterLabel")
        footer.setFont(QFont("微软雅黑", 32, QFont.Bold))
        footer.setStyleSheet("color: #1b5e20; border-top: 2px solid #eee; padding-top: 15px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

# ==============================================================================
# 启动代码块
# ==============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VictoryHeatmapPlugin()
    window.show()
    sys.exit(app.exec_())
