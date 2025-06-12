"""Reusable Qt widgets for Interactive Feedback UI."""
from __future__ import annotations

import base64
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from PySide6.QtCore import QBuffer, QIODevice, Qt, Signal
from PySide6.QtGui import QKeyEvent, QKeySequence, QPixmap
from PySide6.QtWidgets import QApplication, QTextEdit

__all__: List[str] = ["FeedbackTextEdit"]

if TYPE_CHECKING:  # pragma: no cover
    from .main import FeedbackUI  # Avoid runtime circular import


class FeedbackTextEdit(QTextEdit):
    """Rich text editor supporting image paste → base64."""

    # 图片处理常量
    DEFAULT_MAX_IMAGE_WIDTH = 1624
    DEFAULT_MAX_IMAGE_HEIGHT = 1624
    DEFAULT_IMAGE_FORMAT = "PNG"

    # 当用户粘贴图片时发射 pixmap
    image_pasted: Signal = Signal(QPixmap)

    def __init__(self, parent=None):  # noqa: D401, ANN001
        super().__init__(parent)
        self.image_data: list[dict[str, str]] = []  # 保存图片的Base64数据列表
        # 设备像素比，用于 Retina
        self.device_pixel_ratio = QApplication.primaryScreen().devicePixelRatio()
        # 图片压缩/保存参数
        self.max_image_width = self.DEFAULT_MAX_IMAGE_WIDTH
        self.max_image_height = self.DEFAULT_MAX_IMAGE_HEIGHT
        self.image_format = self.DEFAULT_IMAGE_FORMAT

    # ---------------------------------------------------------------------
    # Event handling
    # ---------------------------------------------------------------------
    def keyPressEvent(self, event: QKeyEvent):  # noqa: D401, ANN001
        # Ctrl/Cmd + Enter 提交反馈
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            parent = self.parent()
            # 向上寻找 FeedbackUI
            while parent and parent.__class__.__name__ != "FeedbackUI":
                parent = parent.parent()
            if parent and hasattr(parent, "_submit_feedback"):
                parent._submit_feedback()  # type: ignore[attr-defined]  # pylint: disable=protected-access
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _convert_image_to_base64(self, image):  # noqa: D401, ANN001
        """将 QImage/QPixmap 转为 {data, extension}."""
        try:
            if not isinstance(image, QPixmap):
                pixmap = QPixmap.fromImage(image)
            else:
                pixmap = image

            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)
            pixmap.save(buffer, self.image_format)
            byte_array = buffer.data()
            buffer.close()

            return {
                "data": base64.b64encode(byte_array).decode("utf-8"),
                "extension": self.image_format.lower(),
            }
        except Exception as exc:  # pragma: no cover
            print(f"转换图片为Base64时出错: {exc}")
            return None

    # ------------------------------------------------------------------
    # Paste handling (supports Retina)
    # ------------------------------------------------------------------
    def insertFromMimeData(self, source_data):  # noqa: D401, ANN001
        """捕获图片粘贴，转为 base64 并发射信号."""
        try:
            if source_data.hasImage():
                image = source_data.imageData()
                if image:
                    img_info = self._convert_image_to_base64(image)
                    if img_info:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        unique_id = str(uuid.uuid4())[:8]
                        filename = f"pasted_{timestamp}_{unique_id}.{img_info['extension']}"
                        self.image_data.append({"base64": img_info["data"], "filename": filename})
                        pixmap = image if isinstance(image, QPixmap) else QPixmap.fromImage(image)
                        self.image_pasted.emit(pixmap)
                        return  # 已处理
            # Fallback to default behaviour
            super().insertFromMimeData(source_data)
        except Exception as exc:  # pragma: no cover
            print(f"处理粘贴内容时出错: {exc}")
            try:
                super().insertFromMimeData(source_data)
            except Exception:
                cursor = self.textCursor()
                cursor.insertText(f"[粘贴内容失败: {exc}]")

    # ------------------------------------------------------------------
    def get_image_data(self):  # noqa: D401
        """Return shallow copy of image_data list."""
        return self.image_data.copy()
