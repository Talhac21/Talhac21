import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_telegram(text: str) -> None:
    if not settings.feature_telegram:
        return
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        httpx.post(url, json={"chat_id": settings.telegram_chat_id, "text": text}, timeout=8)
    except Exception as exc:
        logger.warning("Telegram notification failed: %s", exc)
