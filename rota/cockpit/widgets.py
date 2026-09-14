"""
The chat bubble the cockpit mounts, and the two helpers it needs.

Copied from the old TUI's `src/ui/widgets.py` when rota moved to its own
repository. The cockpit reached across the repository root for `ChatMessage`,
through a `sys.path` insert, because the widget lived outside the package. In a
repository that holds only rota there is no outside, so the widget lives here.

Three names came across. `ChatMessage` is the one the cockpit mounts.
`_PreRenderedMarkdown` and `_preprocess_thought_blocks` are the two things it
calls, and neither had another user.
"""
from __future__ import annotations

import re

from rich.markdown import Markdown as _RichMarkdown
from rich.panel import Panel
from textual.widgets import Static


def _preprocess_thought_blocks(text: str) -> str:
    """Turn `<thought>...</thought>` tags into Markdown blockquotes."""
    def _to_blockquote(m: "re.Match") -> str:
        content = m.group(1).strip()
        if not content:
            return ""
        return "\n".join(
            f"> 💭 {line}" if line.strip() else ">"
            for line in content.splitlines()
        )
    return re.sub(r"<thought>(.*?)</thought>", _to_blockquote, text, flags=re.DOTALL)


class _PreRenderedMarkdown:
    """
    A Rich renderable that parses markdown once for each width it is asked for.

    Rich calls `__rich_console__` on every repaint. Rich's own `Markdown`
    renderable parses the source string again every time. That is expensive for
    a large message, and it was the direct cause of a frozen scroll view.

    This wrapper caches the rendered `Segment` list against the width. A dict
    and not one slot, because Textual's layout engine asks for alternating
    widths while it negotiates the scrollbar. Each width renders at most once,
    so an oscillating layout pass never parses without limit.
    """

    _MAX_CACHED_WIDTHS = 8  # a resize-heavy session must not grow without limit

    def __init__(self, markdown_str: str) -> None:
        self._src = markdown_str
        self._cache: dict[int, list] = {}

    def __rich_console__(self, console, options):  # type: ignore[override]
        width = options.max_width
        if width not in self._cache:
            if len(self._cache) >= self._MAX_CACHED_WIDTHS:
                # Remove the oldest entry to keep the memory bounded.
                self._cache.pop(next(iter(self._cache)))
            self._cache[width] = list(
                console.render(_RichMarkdown(self._src), options)
            )
        yield from self._cache[width]


class ChatMessage(Static):
    """
    A chat bubble, built from one `Static` widget and a rendered panel.

    Uses `_PreRenderedMarkdown`, so the markdown source parses at most once for
    each terminal width. A later repaint replays the cached `Segment` list, and
    the scroll latency stays near zero.
    """

    DEFAULT_CSS = """
    ChatMessage {
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        text: str,
        sender: str,
        timestamp: str,
        border_color: str = "blue",
        **kwargs,
    ) -> None:
        processed = _preprocess_thought_blocks(text)
        content = _PreRenderedMarkdown(processed or "[No text returned]")
        panel = Panel(
            content,
            title=f"{sender} [{timestamp}]",
            border_style=border_color,
            expand=True,
        )
        super().__init__(panel, **kwargs)
        self.add_class("chat-message")
