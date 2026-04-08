"""
Telegram Bot API Routes
Webhook and management endpoints for Telegram bot
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import logging

from services.telegram_bot_service import (
    get_telegram_bot,
    alert_subscribers,
    user_chat_ids,
)
from app.deps import get_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])


class AlertMessage(BaseModel):
    """Alert message model"""
    message: str
    alert_type: Optional[str] = "general"


class StockoutAlert(BaseModel):
    """Stockout alert model"""
    product_name: str
    days_until_stockout: int


class PriceAlert(BaseModel):
    """Price change alert model"""
    product_name: str
    old_price: float
    new_price: float


@router.get("/status")
async def get_bot_status():
    """Get Telegram bot status"""
    bot = get_telegram_bot()
    return {
        "is_running": bot.is_running,
        "subscribers_count": len(alert_subscribers),
        "users_count": len(user_chat_ids),
    }


@router.get("/subscribers")
async def get_subscribers(current_user=Depends(get_admin_user)):
    """Get list of alert subscribers (admin only)"""
    return {
        "subscribers": list(alert_subscribers),
        "count": len(alert_subscribers),
    }


@router.post("/send-alert")
async def send_alert(
    alert: AlertMessage,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_admin_user)
):
    """Send alert to all subscribers (admin only)"""
    bot = get_telegram_bot()

    if not bot.is_running:
        raise HTTPException(status_code=503, detail="Telegram bot is not running")

    # Send in background to not block the request
    background_tasks.add_task(bot.send_alert, alert.message)

    return {
        "success": True,
        "message": "Alert scheduled",
        "recipients": len(alert_subscribers),
    }


@router.post("/send-stockout-alert")
async def send_stockout_alert(
    alert: StockoutAlert,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_admin_user)
):
    """Send stockout alert (admin only)"""
    bot = get_telegram_bot()

    if not bot.is_running:
        raise HTTPException(status_code=503, detail="Telegram bot is not running")

    background_tasks.add_task(
        bot.send_stockout_alert,
        alert.product_name,
        alert.days_until_stockout
    )

    return {
        "success": True,
        "message": "Stockout alert scheduled",
        "product": alert.product_name,
    }


@router.post("/send-price-alert")
async def send_price_alert(
    alert: PriceAlert,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_admin_user)
):
    """Send price change alert (admin only)"""
    bot = get_telegram_bot()

    if not bot.is_running:
        raise HTTPException(status_code=503, detail="Telegram bot is not running")

    background_tasks.add_task(
        bot.send_price_alert,
        alert.product_name,
        alert.old_price,
        alert.new_price
    )

    return {
        "success": True,
        "message": "Price alert scheduled",
        "product": alert.product_name,
    }


@router.post("/broadcast")
async def broadcast_message(
    alert: AlertMessage,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_admin_user)
):
    """Broadcast message to all users (admin only)"""
    bot = get_telegram_bot()

    if not bot.is_running:
        raise HTTPException(status_code=503, detail="Telegram bot is not running")

    async def send_to_all():
        for chat_id in user_chat_ids.values():
            try:
                await bot.application.bot.send_message(
                    chat_id=chat_id,
                    text=alert.message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to send to {chat_id}: {e}")

    background_tasks.add_task(send_to_all)

    return {
        "success": True,
        "message": "Broadcast scheduled",
        "recipients": len(user_chat_ids),
    }