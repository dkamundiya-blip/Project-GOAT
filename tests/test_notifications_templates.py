"""
Project GOAT v0.8 — Step 7.7 Notification Templates Dedicated Unit Tests
"""

import json

import pytest

from goat.notifications.core.enums import NotificationType
from goat.notifications.templates.engine import NotificationTemplateEngine


def test_template_rendering_formats():
    tmpl = NotificationTemplateEngine()
    ntype = NotificationType.SIGNAL_GENERATED
    subject = "EURUSD Buy Signal"
    body = "Buy 1.0 lot EURUSD @ 1.0850"
    meta = {"symbol": "EURUSD", "confidence": 0.95}

    md = tmpl.render_markdown(ntype, subject, body, meta)
    assert "# [SIGNAL_GENERATED] EURUSD Buy Signal" in md
    assert "Buy 1.0 lot EURUSD @ 1.0850" in md

    txt = tmpl.render_plain_text(ntype, subject, body, meta)
    assert "[SIGNAL_GENERATED] EURUSD Buy Signal" in txt

    js = tmpl.render_canonical_json(ntype, subject, body, meta)
    parsed = json.loads(js)
    assert parsed["notification_type"] == "SIGNAL_GENERATED"
    assert parsed["subject"] == "EURUSD Buy Signal"

    html = tmpl.render_html(ntype, subject, body, meta)
    assert "<html>" in html
    assert "EURUSD Buy Signal" in html
