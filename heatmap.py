# -*- coding: utf-8 -*-
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from styles import HEATMAP_STYLE

COLOR_LEVELS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

class HeatmapItem(QGraphicsRectItem):
    def __init__(self, x, y, size, minutes, date_str, low_bar=10, parent=None):
        super().__init__(x, y, size, size, parent)
        self.minutes, self.date_str = minutes, date_str
        color_hex = self.get_color(minutes, low_bar)
        self.setBrush(QBrush(QColor(color_hex)))
        self.setPen(QPen(Qt.NoPen))
        self.setAcceptHoverEvents(True)
        self.setToolTip(f"{date_str}\n专注: {minutes} 分钟")

    def get_color(self, mins, low_bar):
        if mins == 0: return COLOR_LEVELS[0]
        if mins < low_bar or mins <= 30: return COLOR_LEVELS[1]
        if mins <= 60: return COLOR_LEVELS[2]
        if mins <= 120: return COLOR_LEVELS[3]
        return COLOR_LEVELS[4]

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.minutes > 0:
            text_color = Qt.white if self.minutes > 60 else QColor("#666666")
            painter.setPen(QPen(text_color))
            painter.setFont(QFont("Segoe UI", 18, QFont.Bold))
            painter.drawText(self.rect(), Qt.AlignCenter, str(int(self.minutes)))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(self.rect().adjusted(6, 4, -5, -5), Qt.AlignTop | Qt.AlignLeft, self.date_str[5:])

class HeatmapView(QGraphicsView):
    def __init__(self, data_map, low_bar=10):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("border: none; background: transparent;")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        item_size, spacing = 95, 15     
        for i, date_str in enumerate(data_map.keys()):
            row, col = i // 5, i % 5
            mins = data_map.get(date_str, 0)
            item = HeatmapItem(col * (item_size + spacing), row * (item_size + spacing), item_size, mins, date_str, low_bar)
            self.scene.addItem(item)

class VictoryHeatmapWindow(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setWindowTitle("🏆 我的成就看板")
        screen = QApplication.primaryScreen().geometry()
        self.resize(int(screen.width() * 0.55), int(screen.height() * 0.9))
        self.setStyleSheet(HEATMAP_STYLE)
        
        self.data_map = self.db.get_heatmap_stats(days=30)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)

        header = QHBoxLayout()
        header.addWidget(QLabel("🌿", font=QFont("Segoe UI Emoji", 70)))
        title_label = QLabel("Focus Heatmap")
        title_label.setObjectName("HeaderTitle")
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        layout.addSpacing(20)

        self.view = HeatmapView(self.data_map)
        layout.addWidget(self.view, alignment=Qt.AlignCenter)
        layout.addStretch(1) 

        # 底边统计栏
        total_all = sum(self.data_map.values())
        footer = QLabel(f"成就达成：近30天共专注 {total_all} 分钟")
        footer.setObjectName("FooterLabel")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)