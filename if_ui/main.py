"""Main UI entry – phase-1 thin wrapper around legacy implementation.

Later commits will gradually migrate the full `FeedbackUI` here.
"""
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from typing import Tuple, Union
    from fastmcp import Image
    FeedbackResult = _legacy.FeedbackResult  # type: ignore
else:
    FeedbackResult = None  # type: ignore


__all__ = ["run_ui", "FeedbackUI", "FeedbackResult"]


# ---------------------------------------------------------------------------
# Phase-2: Start porting FeedbackUI into this module
# ---------------------------------------------------------------------------
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTextBrowser,
    QScrollArea,
    QFrame,
    QCheckBox,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QSizePolicy,
    QGridLayout,
    QFileDialog,
    QGroupBox,
    QRadioButton,
    QSpacerItem,
)
from PySide6.QtGui import QIcon, QKeySequence, QAction, QPixmap, QShortcut, QFont
from PySide6.QtCore import Qt, QSettings, QSize

from .widgets import FeedbackTextEdit
from .theme import get_dark_mode_palette, ModernTheme, ComponentStyles
from .helpers import (
    preprocess_text,
    is_markdown,
    convert_text_to_html,
    convert_markdown_to_html,
)


class FeedbackUI(QMainWindow):
    """现代化的交互式反馈UI界面"""

    def __init__(self, prompt: str, predefined_options: Optional[List[str]] | None = None):
        super().__init__()
        self.prompt = prompt
        self.predefined_options = predefined_options or []

        self.feedback_result = None  # will be set on submit
        self.setWindowTitle("🚀 Cursor 智能交互反馈助手")
        
        # 设置窗口图标
        script_dir = __import__("os").path.dirname(__import__("os").path.abspath(__file__))
        icon_path = __import__("os").path.join(script_dir, "..", "images", "feedback.png")
        self.setWindowIcon(QIcon(icon_path))
        
        # 窗口属性设置
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 设置主题样式表
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {ModernTheme.BG_PRIMARY.name()};
                color: {ModernTheme.TEXT_PRIMARY.name()};
            }}
        """)

        # Settings storage
        self.settings = QSettings("InteractiveFeedbackMCP", "InteractiveFeedbackMCP")

        # Store image preview frames
        self.image_frames: list[QFrame] = []

        # UI init
        self._create_ui()

        # Restore size/position with better defaults
        self._restore_window_state()

        # Connect image pasted signal
        self.feedback_text.image_pasted.connect(self._on_image_pasted)

    def _create_ui(self):
        """创建现代化的用户界面 - 优化布局突出主要功能"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 增加合理间距
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(ModernTheme.SPACING_LG, ModernTheme.SPACING_MD, 
                                 ModernTheme.SPACING_LG, ModernTheme.SPACING_MD)
        layout.setSpacing(ModernTheme.SECTION_SPACING)  # 功能区域间距

        # === 标题区域 ===
        self._create_header(layout)
        
        # === 描述文本区域 ===
        self._create_description_area(layout)
        
        # === 预设选项区域 ===
        if self.predefined_options:
            self._create_options_area(layout)
        
        # === 反馈输入区域 (主要功能) ===
        self._create_feedback_area(layout)
        
        # === 会话控制区域 ===
        self._create_session_control(layout)
        
        # === 图片预览区域 ===
        self._create_image_preview_area(layout)
        
        # === 操作按钮区域 ===
        self._create_action_buttons(layout)
        
        # === 状态栏 ===
        self._create_status_area(layout)

        # 设置快捷键
        self._setup_shortcuts()

    def _create_header(self, layout):
        """创建紧凑但美观的标题区域"""
        header_frame = QFrame()
        header_frame.setFixedHeight(50)  # 固定合理高度
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                           stop: 0 {ModernTheme.PRIMARY.name()}, 
                           stop: 1 {ModernTheme.PRIMARY.darker(120).name()});
                border-radius: {ModernTheme.BORDER_RADIUS}px;
                margin-bottom: 0px;
            }}
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(ModernTheme.SPACING_MD, ModernTheme.SPACING_SM, 
                                       ModernTheme.SPACING_MD, ModernTheme.SPACING_SM)
        
        # 标题标签
        title_label = QLabel("💬 智能交互反馈")
        title_font = QFont()
        title_font.setFamily("system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif")
        title_font.setPointSize(15)  # 适中的字体大小
        title_font.setWeight(QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white; font-weight: bold;")
        
        # 版本标签
        version_label = QLabel("v2.0")
        version_label.setStyleSheet(f"""
            color: {ModernTheme.TEXT_SECONDARY.name()};
            background: rgba(255, 255, 255, 0.15);
            border-radius: {ModernTheme.BORDER_RADIUS_SMALL}px;
            padding: 2px 6px;
            font-size: 11px;
            font-weight: 500;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(version_label)
        
        layout.addWidget(header_frame)

    def _create_description_area(self, layout):
        """创建描述文本区域 - 紧凑但清晰"""
        self.description_text = QTextBrowser()
        
        # 处理文本内容
        processed = preprocess_text(self.prompt)
        html = (
            convert_markdown_to_html(processed)
            if is_markdown(processed)
            else convert_text_to_html(processed)
        )
        self.description_text.setHtml(html)
        
        # 设置属性 - 优化高度分配
        self.description_text.setOpenExternalLinks(True)
        self.description_text.setFrameShape(QFrame.NoFrame)
        self.description_text.setMaximumHeight(200)  # 减少最大高度
        self.description_text.setMinimumHeight(80)   # 减少最小高度
        
        # 应用现代化样式
        self.description_text.setStyleSheet(ComponentStyles.modern_text_browser())
        
        layout.addWidget(self.description_text)

    def _create_options_area(self, layout):
        """创建紧凑的预设选项区域"""
        options_group = QGroupBox("🎯 快速选项")
        options_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 13px;
                font-weight: 600;
                color: {ModernTheme.TEXT_PRIMARY.name()};
                border: 1px solid {ModernTheme.BORDER_DEFAULT.name()};
                border-radius: {ModernTheme.BORDER_RADIUS}px;
                margin-top: {ModernTheme.SPACING_SM}px;
                padding-top: {ModernTheme.SPACING_SM}px;
                background: {ModernTheme.BG_SECONDARY.name()};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {ModernTheme.SPACING_MD}px;
                padding: 0 {ModernTheme.SPACING_SM}px 0 {ModernTheme.SPACING_SM}px;
                background: {ModernTheme.BG_PRIMARY.name()};
                border-radius: {ModernTheme.BORDER_RADIUS_SMALL}px;
            }}
        """)
        
        # 垂直布局，紧凑排列
        group_layout = QVBoxLayout(options_group)
        group_layout.setContentsMargins(ModernTheme.SPACING_MD, ModernTheme.SPACING_SM, 
                                      ModernTheme.SPACING_MD, ModernTheme.SPACING_SM)
        group_layout.setSpacing(ModernTheme.SPACING_SM)  # 适中的行间距

        # 创建复选框 - 垂直排列
        self.option_checkboxes: list[QCheckBox] = []
        for opt in self.predefined_options:
            cb = QCheckBox(opt)
            cb.setStyleSheet(f"""
            QCheckBox {{
                color: {ModernTheme.TEXT_PRIMARY.name()};
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 13px;
                font-weight: 500;
                spacing: {ModernTheme.SPACING_SM}px;
                padding: {ModernTheme.SPACING_XS}px 0px;
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
            }}
            """)
            self.option_checkboxes.append(cb)
            group_layout.addWidget(cb)
        
        layout.addWidget(options_group)

    def _create_feedback_area(self, layout):
        """创建反馈输入区域 - 彻底解决双边框问题"""
        feedback_group = QGroupBox("✍️ 详细反馈 (主要功能)")
        feedback_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: 700;
                color: {ModernTheme.PRIMARY.name()};
                border: none;  /* 完全移除边框 */
                border-radius: 0px;
                margin-top: {ModernTheme.SPACING_MD}px;
                padding-top: {ModernTheme.SPACING_MD}px;
                background: transparent;  /* 透明背景 */
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 0px;
                padding: 0 {ModernTheme.SPACING_SM}px 0 0px;
                background: transparent;
                border-radius: 0px;
            }}
        """)
        
        group_layout = QVBoxLayout(feedback_group)
        group_layout.setContentsMargins(0, ModernTheme.SPACING_SM, 0, 0)  # 只保留顶部间距
        group_layout.setSpacing(ModernTheme.SPACING_SM)
        
        # 反馈文本编辑器 - 恢复边框作为唯一的视觉边界
        self.feedback_text = FeedbackTextEdit()
        self.feedback_text.setPlaceholderText("💭 请输入您的详细反馈和建议... (支持 Ctrl+Enter 快速提交，支持粘贴图片)")
        self.feedback_text.setMinimumHeight(120)
        self.feedback_text.setMaximumHeight(200)
        
        # 应用现代化样式 - TextEdit作为主要的视觉容器
        self.feedback_text.setStyleSheet(f"""
        QTextEdit {{
            background-color: {ModernTheme.BG_CARD.name()};
            border: 2px solid {ModernTheme.PRIMARY.name()};  /* 恢复主要边框 */
            border-radius: {ModernTheme.BORDER_RADIUS}px;
            padding: {ModernTheme.SPACING_MD}px;
            color: {ModernTheme.TEXT_PRIMARY.name()};
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
            font-size: 14px;
            line-height: 1.5;
            selection-background-color: {ModernTheme.PRIMARY.name()};
        }}
        QTextEdit:focus {{
            background-color: {ModernTheme.BG_CARD.lighter(110).name()};
            border-color: {ModernTheme.PRIMARY.lighter(120).name()};
        }}
        QTextEdit:hover {{
            border-color: {ModernTheme.PRIMARY.lighter(110).name()};
        }}
        """)
        
        group_layout.addWidget(self.feedback_text)
        layout.addWidget(feedback_group)

    def _create_session_control(self, layout):
        """创建清晰的会话控制区域 - 修复字体遮挡问题"""
        session_group = QGroupBox("🔄 会话控制")
        session_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 13px;
                font-weight: 600;
                color: {ModernTheme.TEXT_PRIMARY.name()};
                border: 1px solid {ModernTheme.BORDER_DEFAULT.name()};
                border-radius: {ModernTheme.BORDER_RADIUS}px;
                margin-top: {ModernTheme.SPACING_SM}px;
                padding-top: {ModernTheme.SPACING_MD}px;  /* 增加顶部padding */
                background: {ModernTheme.BG_SECONDARY.name()};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {ModernTheme.SPACING_MD}px;
                padding: 0 {ModernTheme.SPACING_SM}px 0 {ModernTheme.SPACING_SM}px;
                background: {ModernTheme.BG_PRIMARY.name()};
                border-radius: {ModernTheme.BORDER_RADIUS_SMALL}px;
            }}
        """)
        session_group.setFixedHeight(90)  # 增加高度从70到90
        
        sess_layout = QHBoxLayout(session_group)
        sess_layout.setContentsMargins(ModernTheme.SPACING_LG, ModernTheme.SPACING_LG, 
                                     ModernTheme.SPACING_LG, ModernTheme.SPACING_MD)  # 增加顶部内边距
        sess_layout.setSpacing(ModernTheme.SPACING_XL)  # 适中的按钮间距
        
        # 单选按钮样式 - 确保文字完全显示
        radio_style = f"""
        QRadioButton {{
            color: {ModernTheme.TEXT_PRIMARY.name()};
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            font-weight: 600;
            spacing: {ModernTheme.SPACING_MD}px;
            padding: {ModernTheme.SPACING_SM}px;
            min-height: 24px;  /* 确保最小高度 */
        }}
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 2px solid {ModernTheme.BORDER_DEFAULT.name()};
            background: {ModernTheme.BG_CARD.name()};
            margin-right: {ModernTheme.SPACING_MD}px;
        }}
        QRadioButton::indicator:hover {{
            border-color: {ModernTheme.PRIMARY.name()};
            background: {ModernTheme.BG_TERTIARY.name()};
        }}
        QRadioButton::indicator:checked {{
            background: {ModernTheme.PRIMARY.name()};
            border-color: {ModernTheme.PRIMARY.name()};
        }}
        """
        
        self.rb_continue = QRadioButton("📝 继续会话")
        self.rb_terminate = QRadioButton("🔚 终止会话")
        
        self.rb_continue.setStyleSheet(radio_style)
        self.rb_terminate.setStyleSheet(radio_style)
        self.rb_continue.setChecked(True)
        
        sess_layout.addWidget(self.rb_continue)
        sess_layout.addWidget(self.rb_terminate)
        sess_layout.addStretch(1)
        
        layout.addWidget(session_group)

    def _create_image_preview_area(self, layout):
        """创建紧凑的图片预览区域"""
        # 图片预览滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setVisible(False)  # 默认隐藏
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(80)  # 从100减小到80
        self.scroll_area.setStyleSheet(ComponentStyles.modern_scroll_area())

        self.images_container = QWidget()
        self.images_container.setStyleSheet(f"""
            QWidget {{
                background: {ModernTheme.BG_CARD.name()};
                border-radius: {ModernTheme.BORDER_RADIUS}px;
            }}
        """)
        
        self.images_layout = QHBoxLayout(self.images_container)
        self.images_layout.setContentsMargins(ModernTheme.SPACING_XS, ModernTheme.SPACING_XS, 
                                            ModernTheme.SPACING_XS, ModernTheme.SPACING_XS)
        self.images_layout.setSpacing(ModernTheme.SPACING_XS)
        self.images_layout.addStretch(1)

        self.scroll_area.setWidget(self.images_container)
        layout.addWidget(self.scroll_area)

    def _create_action_buttons(self, layout):
        """创建突出的操作按钮区域"""
        button_frame = QFrame()
        button_frame.setStyleSheet(f"""
            QFrame {{
                background: {ModernTheme.BG_SECONDARY.name()};
                border: 1px solid {ModernTheme.BORDER_DEFAULT.name()};
                border-radius: {ModernTheme.BORDER_RADIUS}px;
                padding: {ModernTheme.SPACING_MD}px;
            }}
        """)
        
        btn_layout = QHBoxLayout(button_frame)
        btn_layout.setContentsMargins(ModernTheme.SPACING_MD, ModernTheme.SPACING_SM, 
                                    ModernTheme.SPACING_MD, ModernTheme.SPACING_SM)
        btn_layout.setSpacing(ModernTheme.SPACING_MD)

        # 添加图片按钮
        upload_btn = QPushButton("📷 添加图片")
        upload_btn.setStyleSheet(ComponentStyles.modern_button("secondary", "medium"))
        upload_btn.clicked.connect(self._on_add_images)

        # 提交按钮 - 突出显示
        submit_btn = QPushButton("🚀 提交反馈")
        submit_btn.setStyleSheet(ComponentStyles.modern_button("primary", "large"))
        submit_btn.clicked.connect(self._submit_feedback)
        submit_btn.setDefault(True)  # 设为默认按钮

        # 取消按钮
        cancel_btn = QPushButton("❌ 取消")
        cancel_btn.setStyleSheet(ComponentStyles.modern_button("secondary", "medium"))
        cancel_btn.clicked.connect(self.close)

        btn_layout.addWidget(upload_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(submit_btn)

        layout.addWidget(button_frame)

    def _create_status_area(self, layout):
        """创建紧凑的状态栏"""
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-top: 1px solid {ModernTheme.BORDER_DEFAULT.name()};
                padding-top: {ModernTheme.SPACING_SM}px;
            }}
        """)
        
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(0, ModernTheme.SPACING_SM, 0, 0)
        
        # 快捷键提示
        shortcuts_label = QLabel("💡 Ctrl+Enter 提交 | Cmd+/- 字体 | Esc 取消")
        shortcuts_label.setStyleSheet(f"""
            color: {ModernTheme.TEXT_MUTED.name()};
            font-size: 11px;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        """)
        
        # 版权信息
        credit_label = QLabel("Enhanced by Cursor AI")
        credit_label.setStyleSheet(f"""
            color: {ModernTheme.TEXT_MUTED.name()};
            font-size: 10px;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        """)
        
        status_layout.addWidget(shortcuts_label)
        status_layout.addStretch()
        status_layout.addWidget(credit_label)
        
        layout.addWidget(status_frame)

    # ------------------------------------------------------------------
    # Shortcuts and Event Handling
    # ------------------------------------------------------------------
    def _setup_shortcuts(self):
        """设置快捷键"""
        # 字体缩放
        zoom_in = QAction(self)
        zoom_in.setShortcuts([QKeySequence("Ctrl+="), QKeySequence("Ctrl++")])
        zoom_in.triggered.connect(lambda: self._adjust_font(1.1))
        self.addAction(zoom_in)
        
        zoom_out = QAction(self)
        zoom_out.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out.triggered.connect(lambda: self._adjust_font(0.9))
        self.addAction(zoom_out)
        
        reset_zoom = QAction(self)
        reset_zoom.setShortcut(QKeySequence("Ctrl+0"))
        reset_zoom.triggered.connect(lambda: self._adjust_font(reset=True))
        self.addAction(reset_zoom)

        # 窗口控制
        for seq in ["Esc", "Ctrl+W", "Meta+W"]:
            close_action = QAction(self)
            close_action.setShortcut(QKeySequence(seq))
            close_action.triggered.connect(self.close)
            self.addAction(close_action)
            
        for seq in ["Ctrl+Q", "Meta+Q"]:
            quit_action = QAction(self)
            quit_action.setShortcut(QKeySequence(seq))
            quit_action.triggered.connect(QApplication.instance().quit)
            self.addAction(quit_action)

        # 提交快捷键
        for seq in ["Ctrl+Return", "Meta+Return", "Ctrl+Enter", "Meta+Enter"]:
            submit_shortcut = QShortcut(QKeySequence(seq), self)
            submit_shortcut.activated.connect(self._submit_feedback)

    def _adjust_font(self, factor: float = 1.0, reset: bool = False):
        """调整界面字体大小"""
        app = QApplication.instance()
        current_font = app.font()
        
        if reset:
            # 重置为默认字体大小
            current_font.setPointSize(13)
        else:
            current_size = current_font.pointSize()
            new_size = max(8, min(24, int(current_size * factor)))
            current_font.setPointSize(new_size)
        
        app.setFont(current_font)

    def _submit_feedback(self):
        """提交反馈"""
        feedback_text = self.feedback_text.toPlainText().strip()
        
        # 收集选中的选项
        selected_options = []
        for cb in self.option_checkboxes:
            if cb.isChecked():
                selected_options.append(cb.text())
        
        # 组合反馈内容
        if selected_options:
            options_text = "选择的选项:\n" + "\n".join(f"✓ {opt}" for opt in selected_options)
            if feedback_text:
                feedback_text = f"{options_text}\n\n详细反馈:\n{feedback_text}"
            else:
                feedback_text = options_text
        
        # 获取图片数据
        image_data = self.feedback_text.get_image_data()
        image_b64_list = [img["base64"] for img in image_data]
        
        # 保存结果
        self.feedback_result = {
            "interactive_feedback": feedback_text,
            "images": image_b64_list
        }
        
        self.close()

    def run(self):
        """运行UI并返回结果"""
        self.show()
        QApplication.instance().exec()
        return self.feedback_result

    def _restore_window_state(self):
        """恢复窗口状态"""
        # 设置更好的默认窗口尺寸
        screen = QApplication.primaryScreen().geometry()
        default_width = min(900, int(screen.width() * 0.6))
        default_height = min(700, int(screen.height() * 0.7))
        
        # 恢复几何信息，如果不存在则使用默认值
        self.settings.beginGroup("MainWindow_General")
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(default_width, default_height)
            # 居中显示
            x = (screen.width() - default_width) // 2
            y = (screen.height() - default_height) // 2
            self.move(x, y)
        self.settings.endGroup()

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存几何信息
        self.settings.beginGroup("MainWindow_General")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.endGroup()
        
        event.accept()

    def _on_image_pasted(self, pixmap: QPixmap):
        """处理图片粘贴事件"""
        # 创建图片预览框架
        image_frame = QFrame()
        image_frame.setFixedSize(80, 80)
        image_frame.setStyleSheet(f"""
            QFrame {{
                background: {ModernTheme.BG_TERTIARY.name()};
                border: 2px solid {ModernTheme.BORDER_DEFAULT.name()};
                border-radius: {ModernTheme.BORDER_RADIUS_SMALL}px;
                padding: 4px;
            }}
            QFrame:hover {{
                border-color: {ModernTheme.BORDER_HOVER.name()};
            }}
        """)
        
        # 图片布局
        frame_layout = QVBoxLayout(image_frame)
        frame_layout.setContentsMargins(4, 4, 4, 4)
        frame_layout.setSpacing(2)
        
        # 缩放图片
        scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # 图片标签
        image_label = QLabel()
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("border: none; background: transparent;")
        
        # 删除按钮
        delete_btn = QToolButton()
        delete_btn.setText("🗑️")
        delete_btn.setStyleSheet(f"""
            QToolButton {{
                background: {ModernTheme.ERROR.name()};
                color: white;
                border: none;
                border-radius: {ModernTheme.BORDER_RADIUS_SMALL}px;
                font-size: 10px;
                max-width: 20px;
                max-height: 16px;
            }}
            QToolButton:hover {{
                background: {ModernTheme.ERROR.darker(120).name()};
            }}
        """)
        delete_btn.clicked.connect(lambda: self._delete_image_frame(image_frame))
        
        frame_layout.addWidget(image_label)
        frame_layout.addWidget(delete_btn)
        
        # 添加到图片容器
        self.image_frames.append(image_frame)
        self.images_layout.insertWidget(self.images_layout.count() - 1, image_frame)
        
        # 显示图片预览区域
        self.scroll_area.setVisible(True)

    def _delete_image_frame(self, frame: QFrame):
        """删除图片预览框架"""
        if frame in self.image_frames:
            # 从UI中移除
            self.images_layout.removeWidget(frame)
            frame.deleteLater()
            
            # 从列表中移除
            frame_index = self.image_frames.index(frame)
            self.image_frames.remove(frame)
            
            # 从图片数据中移除对应项
            if frame_index < len(self.feedback_text.image_data):
                self.feedback_text.image_data.pop(frame_index)
            
            # 如果没有图片了，隐藏预览区域
            if not self.image_frames:
                self.scroll_area.setVisible(False)

    def _on_add_images(self):
        """通过文件对话框添加图片"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图片文件",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;所有文件 (*)"
        )
        
        for file_path in file_paths:
            try:
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # 转换为Base64并添加到图片数据
                    import base64
                    from PySide6.QtCore import QBuffer, QIODevice
                    
                    buffer = QBuffer()
                    buffer.open(QIODevice.WriteOnly)
                    pixmap.save(buffer, "PNG")
                    
                    b64_data = base64.b64encode(buffer.data()).decode('utf-8')
                    filename = __import__("os").path.basename(file_path)
                    
                    self.feedback_text.image_data.append({
                        'base64': b64_data,
                        'filename': filename
                    })
                    
                    # 触发图片预览
                    self._on_image_pasted(pixmap)
                    
            except Exception as e:
                print(f"加载图片失败 {file_path}: {e}")


def run_ui(prompt: str, predefined_options: Optional[List[str]] | None = None):
    """运行现代化UI界面"""
    import sys
    
    # 创建应用程序（如果不存在）
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("Interactive Feedback MCP")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("InteractiveFeedbackMCP")
    
    # 启用高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 应用暗色主题
    app.setPalette(get_dark_mode_palette(app))
    
    # 设置全局字体
    font = QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif")
    font.setPointSize(13)
    app.setFont(font)
    
    # 设置全局样式表
    app.setStyleSheet(f"""
        QToolTip {{
            background-color: {ModernTheme.BG_TERTIARY.name()};
            color: {ModernTheme.TEXT_PRIMARY.name()};
            border: 1px solid {ModernTheme.BORDER_DEFAULT.name()};
            border-radius: {ModernTheme.BORDER_RADIUS_SMALL}px;
            padding: 4px;
            font-size: 12px;
        }}
    """)
    
    # 创建并运行UI
    ui = FeedbackUI(prompt, predefined_options)
    return ui.run()

# Re-export for external import paths
FeedbackUI = FeedbackUI  # type: ignore


# ---------------------------------------------------------------------------
# CLI entry (python -m if_ui.main)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Interactive Feedback UI")
    parser.add_argument("--prompt", default="我已经根据您的请求完成了修改。", help="Prompt text displayed to the user")
    parser.add_argument("--predefined-options", default="", help="Preset options separated by |||")
    args = parser.parse_args()

    options = [opt for opt in args.predefined_options.split("|||") if opt] if args.predefined_options else None

    # Ensure High DPI attributes (apply *before* QApplication instance)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setPalette(get_dark_mode_palette(app))
    app.setStyle("Fusion")
    default_font = app.font()
    default_font.setPointSize(15)
    app.setFont(default_font)

    ui = FeedbackUI(args.prompt, options)
    ui.show()

    app.exec()
    result = ui.feedback_result or {"interactive_feedback": "", "images": []}
    print("\n收到的反馈:\n", result["interactive_feedback"]) 
