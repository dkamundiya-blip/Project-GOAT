"""
Project GOAT v0.8 — Notification Template Engine

Provides deterministic immutable template rendering across Markdown, Plain Text, Canonical JSON, and HTML formats.
"""

from __future__ import annotations

import json
from typing import Any

from goat.notifications.core.enums import NotificationType


class NotificationTemplateEngine:
    """Deterministic template rendering engine for notification formatting."""

    def render_markdown(self, notification_type: NotificationType | str, subject: str, body: str, metadata: dict[str, Any] | None = None) -> str:
        """Render Markdown notification text."""
        ntype = notification_type.value if hasattr(notification_type, "value") else str(notification_type)
        meta_lines = []
        if metadata:
            for k, v in sorted(metadata.items()):
                meta_lines.append(f"- **{k}**: `{v}`")
        meta_block = "\n".join(meta_lines) if meta_lines else "- *No extra metadata*"

        return f"""# [{ntype}] {subject}

{body}

### Metadata
{meta_block}
"""

    def render_plain_text(self, notification_type: NotificationType | str, subject: str, body: str, metadata: dict[str, Any] | None = None) -> str:
        """Render Plain Text notification."""
        ntype = notification_type.value if hasattr(notification_type, "value") else str(notification_type)
        meta_str = f" | Metadata: {json.dumps(metadata, sort_keys=True)}" if metadata else ""
        return f"[{ntype}] {subject}\n{body}{meta_str}"

    def render_canonical_json(self, notification_type: NotificationType | str, subject: str, body: str, metadata: dict[str, Any] | None = None) -> str:
        """Render Canonical JSON notification."""
        ntype = notification_type.value if hasattr(notification_type, "value") else str(notification_type)
        payload = {
            "body": body,
            "metadata": metadata or {},
            "notification_type": ntype,
            "subject": subject,
        }
        return json.dumps(payload, indent=2, sort_keys=True)

    def render_html(self, notification_type: NotificationType | str, subject: str, body: str, metadata: dict[str, Any] | None = None) -> str:
        """Render HTML notification format."""
        ntype = notification_type.value if hasattr(notification_type, "value") else str(notification_type)
        return f"""<!DOCTYPE html>
<html>
<head><title>{subject}</title></head>
<body>
  <h2>[{ntype}] {subject}</h2>
  <p>{body}</p>
</body>
</html>
"""
