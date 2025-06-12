"""现代化主题和样式系统 for Interactive Feedback UI."""
from __future__ import annotations

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

__all__ = ["get_dark_mode_palette", "ModernTheme", "ComponentStyles"]


class ModernTheme:
    """现代化主题颜色系统"""
    
    # 主色调
    PRIMARY = QColor(64, 158, 255)        # 现代蓝色
    PRIMARY_HOVER = QColor(89, 176, 255)  # 悬停蓝色
    PRIMARY_PRESSED = QColor(45, 140, 230) # 按下蓝色
    
    # 次要色调
    SECONDARY = QColor(156, 163, 175)     # 现代灰色
    SECONDARY_HOVER = QColor(107, 114, 128)
    SECONDARY_PRESSED = QColor(75, 85, 99)
    
    # 背景色系
    BG_PRIMARY = QColor(30, 30, 35)       # 主背景 - 更深
    BG_SECONDARY = QColor(40, 40, 45)     # 次背景
    BG_TERTIARY = QColor(50, 50, 55)      # 第三背景
    BG_CARD = QColor(45, 45, 50)          # 卡片背景
    
    # 文本色系
    TEXT_PRIMARY = QColor(255, 255, 255)   # 主文本
    TEXT_SECONDARY = QColor(200, 200, 200) # 次文本
    TEXT_MUTED = QColor(150, 150, 150)     # 弱化文本
    TEXT_PLACEHOLDER = QColor(120, 120, 120) # 占位符文本
    
    # 边框色系
    BORDER_DEFAULT = QColor(70, 70, 75)    # 默认边框
    BORDER_FOCUS = QColor(64, 158, 255)    # 聚焦边框
    BORDER_HOVER = QColor(90, 90, 95)      # 悬停边框
    
    # 状态色系
    SUCCESS = QColor(34, 197, 94)          # 成功绿色
    WARNING = QColor(251, 191, 36)         # 警告黄色
    ERROR = QColor(239, 68, 68)            # 错误红色
    
    # 设计常量 - 重新平衡间距，突出主要功能
    BORDER_RADIUS = 8
    BORDER_RADIUS_SMALL = 4
    BORDER_RADIUS_LARGE = 12
    
    # 增加间距让界面有呼吸感，但保持紧凑
    SPACING_XS = 4      # 最小间距
    SPACING_SM = 8      # 小间距  
    SPACING_MD = 16     # 中等间距 - 主要功能区域
    SPACING_LG = 24     # 大间距 - 重要分隔
    SPACING_XL = 32     # 超大间距 - 顶级分隔
    
    # 功能区域专用间距
    SECTION_SPACING = 20     # 功能区域间距
    CONTENT_PADDING = 12     # 内容区域内边距
    
    SHADOW_LIGHT = "0 1px 3px rgba(0, 0, 0, 0.12)"
    SHADOW_MEDIUM = "0 4px 6px rgba(0, 0, 0, 0.1)"
    SHADOW_HEAVY = "0 8px 16px rgba(0, 0, 0, 0.15)"


class ComponentStyles:
    """组件样式集合"""
    
    @staticmethod
    def modern_button(color_type="primary", size="medium"):
        """现代化按钮样式"""
        if color_type == "primary":
            bg_color = ModernTheme.PRIMARY.name()
            hover_color = ModernTheme.PRIMARY_HOVER.name()
            pressed_color = ModernTheme.PRIMARY_PRESSED.name()
        else:  # secondary
            bg_color = ModernTheme.SECONDARY.name()
            hover_color = ModernTheme.SECONDARY_HOVER.name()
            pressed_color = ModernTheme.SECONDARY_PRESSED.name()
        
        padding = "10px 20px" if size == "large" else "8px 16px"
        font_size = "14px" if size == "large" else "13px"
        
        return f"""
        QPushButton {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 {bg_color}, 
                                      stop: 1 {QColor(bg_color).darker(110).name()});
            color: white;
            border: none;
            border-radius: {ModernTheme.BORDER_RADIUS}px;
            padding: {padding};
            font-size: {font_size};
            font-weight: 500;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 {hover_color}, 
                                      stop: 1 {QColor(hover_color).darker(110).name()});
        }}
        QPushButton:pressed {{
            background: {pressed_color};
        }}
        QPushButton:disabled {{
            background: {ModernTheme.BG_TERTIARY.name()};
            color: {ModernTheme.TEXT_MUTED.name()};
        }}
        """
    
    @staticmethod
    def modern_text_edit():
        """现代化文本编辑器样式"""
        return f"""
        QTextEdit {{
            background-color: {ModernTheme.BG_CARD.name()};
            border: 2px solid {ModernTheme.BORDER_DEFAULT.name()};
            border-radius: {ModernTheme.BORDER_RADIUS}px;
            padding: {ModernTheme.SPACING_MD}px;
            color: {ModernTheme.TEXT_PRIMARY.name()};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
            font-size: 14px;
            line-height: 1.5;
            selection-background-color: {ModernTheme.PRIMARY.name()};
        }}
        QTextEdit:focus {{
            border-color: {ModernTheme.BORDER_FOCUS.name()};
            background-color: {ModernTheme.BG_CARD.lighter(105).name()};
        }}
        QTextEdit:hover {{
            border-color: {ModernTheme.BORDER_HOVER.name()};
        }}
        """
    
    @staticmethod
    def modern_text_browser():
        """现代化文本浏览器样式"""
        return f"""
        QTextBrowser {{
            background-color: {ModernTheme.BG_SECONDARY.name()};
            border: 1px solid {ModernTheme.BORDER_DEFAULT.name()};
            border-radius: {ModernTheme.BORDER_RADIUS}px;
            padding: {ModernTheme.SPACING_MD}px;
            color: {ModernTheme.TEXT_PRIMARY.name()};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            selection-background-color: {ModernTheme.PRIMARY.name()};
        }}
        QTextBrowser:focus {{
            border-color: {ModernTheme.BORDER_FOCUS.name()};
        }}
        """
    
    @staticmethod
    def modern_checkbox():
        """现代化复选框样式 - 适合垂直排列"""
        return f"""
        QCheckBox {{
            color: {ModernTheme.TEXT_PRIMARY.name()};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            font-weight: 500;
            spacing: {ModernTheme.SPACING_SM}px;
            padding: {ModernTheme.SPACING_XS}px 0px;  /* 上下padding让行高更舒适 */
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: {ModernTheme.BORDER_RADIUS_SMALL}px;
            border: 2px solid {ModernTheme.BORDER_DEFAULT.name()};
            background: {ModernTheme.BG_CARD.name()};
            margin-right: {ModernTheme.SPACING_SM}px;
        }}
        QCheckBox::indicator:hover {{
            border-color: {ModernTheme.BORDER_HOVER.name()};
            background: {ModernTheme.BG_TERTIARY.name()};
        }}
        QCheckBox::indicator:checked {{
            background: {ModernTheme.PRIMARY.name()};
            border-color: {ModernTheme.PRIMARY.name()};
            image: none;
        }}
        QCheckBox::indicator:checked::after {{
            content: '✓';
            color: white;
            font-size: 12px;
            font-weight: bold;
            text-align: center;
            line-height: 16px;
        }}
        """
    
    @staticmethod
    def modern_group_box():
        """现代化组框样式 - 零边距版本"""
        return f"""
        QGroupBox {{
            font-size: 13px;
            font-weight: 600;
            color: {ModernTheme.TEXT_PRIMARY.name()};
            border: 1px solid {ModernTheme.BORDER_DEFAULT.name()};
            border-radius: {ModernTheme.BORDER_RADIUS}px;
            margin-top: 0px;  /* 完全移除顶部边距 */
            margin-bottom: 0px;  /* 移除底部边距 */
            background: {ModernTheme.BG_CARD.name()};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px 0 4px;  /* 减小标题padding */
            background: {ModernTheme.BG_CARD.name()};
        }}
        """
    
    @staticmethod 
    def modern_scroll_area():
        """现代化滚动区域样式"""
        return f"""
        QScrollArea {{
            background: transparent;
            border: none;
        }}
        QScrollBar:horizontal {{
            height: 8px;
            background: {ModernTheme.BG_TERTIARY.name()};
            border-radius: 4px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {ModernTheme.SECONDARY.name()};
            border-radius: 4px;
            min-width: 20px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {ModernTheme.SECONDARY_HOVER.name()};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        QScrollBar:vertical {{
            width: 8px;
            background: {ModernTheme.BG_TERTIARY.name()};
            border-radius: 4px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {ModernTheme.SECONDARY.name()};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {ModernTheme.SECONDARY_HOVER.name()};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """


def get_dark_mode_palette(app: QApplication) -> QPalette:
    """返回现代化的暗色主题调色板"""
    dark_palette = app.palette()
    
    # 使用 ModernTheme 的颜色
    dark_palette.setColor(QPalette.Window, ModernTheme.BG_PRIMARY)
    dark_palette.setColor(QPalette.WindowText, ModernTheme.TEXT_PRIMARY)
    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, ModernTheme.TEXT_MUTED)
    dark_palette.setColor(QPalette.Base, ModernTheme.BG_CARD)
    dark_palette.setColor(QPalette.AlternateBase, ModernTheme.BG_SECONDARY)
    dark_palette.setColor(QPalette.ToolTipBase, ModernTheme.BG_TERTIARY)
    dark_palette.setColor(QPalette.ToolTipText, ModernTheme.TEXT_PRIMARY)
    dark_palette.setColor(QPalette.Text, ModernTheme.TEXT_PRIMARY)
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, ModernTheme.TEXT_MUTED)
    dark_palette.setColor(QPalette.Dark, ModernTheme.BG_PRIMARY.darker(120))
    dark_palette.setColor(QPalette.Shadow, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.Button, ModernTheme.BG_TERTIARY)
    dark_palette.setColor(QPalette.ButtonText, ModernTheme.TEXT_PRIMARY)
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, ModernTheme.TEXT_MUTED)
    dark_palette.setColor(QPalette.BrightText, ModernTheme.ERROR)
    dark_palette.setColor(QPalette.Link, ModernTheme.PRIMARY)
    dark_palette.setColor(QPalette.Highlight, ModernTheme.PRIMARY)
    dark_palette.setColor(QPalette.Disabled, QPalette.Highlight, ModernTheme.BG_TERTIARY)
    dark_palette.setColor(QPalette.HighlightedText, ModernTheme.TEXT_PRIMARY)
    dark_palette.setColor(QPalette.Disabled, QPalette.HighlightedText, ModernTheme.TEXT_MUTED)
    dark_palette.setColor(QPalette.PlaceholderText, ModernTheme.TEXT_PLACEHOLDER)
    
    return dark_palette
