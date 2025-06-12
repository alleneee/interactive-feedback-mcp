"""Interactive Feedback UI package.
Provides run_ui entrypoint to show Feedback UI.
"""
from importlib import import_module
from types import ModuleType
from typing import Optional, List, TypedDict, Tuple, Union

# Dynamically import original monolithic module to keep backward compatibility
_original: ModuleType = import_module("feedback_ui")

FeedbackResult = _original.FeedbackResult  # type: ignore

# Re-export commonly used symbols
get_dark_mode_palette = _original.get_dark_mode_palette  # type: ignore
FeedbackTextEdit = _original.FeedbackTextEdit  # type: ignore
FeedbackUI = _original.FeedbackUI  # type: ignore

# Public API

def run_ui(prompt: str, predefined_options: Optional[List[str]] | None = None) -> FeedbackResult:  # type: ignore
    """Wrapper around original feedback_ui.feedback_ui to preserve behaviour.
    This enables future refactor: internal implementation can move while external call sites stay the same.
    """
    return _original.feedback_ui(prompt, predefined_options)
