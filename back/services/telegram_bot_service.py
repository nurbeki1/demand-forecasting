"""
Forecast AI — Telegram қолдау боты (адам оператор арқылы).

Қолданушы: inline түймелер — «Отзыв» / «Запрос» → мәселені жібереді → растау хабарламасы ғана (AI жоқ).
Операторлар: TELEGRAM_SUPPORT_GROUP_ID ішкі топта бот жіберген хабарламаға *reply* жасап жауап береді —
жауап сол қолданушыға қайта жіберіледі.

Қосымша: /forecast, /price, /report, /alerts, /cities (AI қолданылады).
"""

import html
import os
import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatType
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

logger = logging.getLogger(__name__)

# Bot token from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Store user chat IDs for notifications
user_chat_ids: dict[str, int] = {}

# Alert subscribers
alert_subscribers: set[int] = set()

# Боттың қолдау топындағы хабарлама id → пайдаланушының жеке chat id (ресүрстан кейін тазарады).
_ticket_bridge: dict[int, int] = {}


def _support_group_id() -> Optional[int]:
    raw = (os.getenv("TELEGRAM_SUPPORT_GROUP_ID") or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        logger.warning("TELEGRAM_SUPPORT_GROUP_ID must be an integer (e.g. -100...)")
        return None


def _operator_id_set() -> Optional[set[int]]:
    raw = (os.getenv("TELEGRAM_SUPPORT_OPERATOR_IDS") or "").strip()
    if not raw:
        return None
    ids: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            ids.add(int(part))
    return ids if ids else None


def _is_operator(user_id: int) -> bool:
    allowed = _operator_id_set()
    if allowed is None:
        return True
    return user_id in allowed


def support_menu_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⭐ Отзыв", callback_data="support:feedback"),
                InlineKeyboardButton("📩 Запрос", callback_data="support:request"),
            ]
        ]
    )


def _support_contact_block_markdown() -> str:
    """FRONTEND_URL / SUPPORT_EMAIL — қолдау контактілері (Markdown)."""
    web = (os.getenv("FRONTEND_URL") or "").strip().rstrip("/")
    email = (os.getenv("SUPPORT_EMAIL") or "").strip().replace("`", "")
    parts: list[str] = []
    if web:
        parts.append(f"🌐 [Веб-қосымша]({web})")
    if email:
        parts.append(f"✉️ [{email}](mailto:{email})")
    if not parts:
        parts.append(
            "_Әкімшіге айтыңыз:_ осында `FRONTEND_URL` және қажет болса `SUPPORT_EMAIL` орнатылады."
        )
    return "\n".join(parts)


class TelegramBotService:
    """Telegram — қолдау интерфейсі + болжамдық автоматтандыру."""

    def __init__(self):
        self.application: Optional[Application] = None
        self.is_running = False

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat_id = update.effective_chat.id

        # Store user
        user_chat_ids[str(user.id)] = chat_id

        links = _support_contact_block_markdown()
        deep = ""
        if context.args and context.args[0].strip().lower() == "support":
            deep = "\n_Сізді қолдау арнасына бағыттадық._\n"

        welcome_message = f"""
🛟 *Forecast AI — қолдау*{deep}

Сәлем, *{user.first_name}*!

Төменде түрді таңдаңыз, содан кейін *бір хабарламада* мәселеңізді жіберіңіз (мәтін немесе скрин).
Жауапты *оператор осы чатта* жазады (авто-жауап жоқ).

📎 *Байланыс (қосымша):*
{links}

📊 Болжам құралдары: `/help`
"""
        await update.message.reply_text(
            welcome_message,
            parse_mode="Markdown",
            reply_markup=support_menu_markup(),
        )

    async def support_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Қолдау: Отзыв / Запрос таңдау."""
        links = _support_contact_block_markdown()
        text = f"""
🛟 *Қолдау*

Түймелерден *Отзыв* немесе *Запрос* таңдаңыз, содан кейін хабарламаңызды жіберіңіз.

Оператор жауабын күтіңіз.

📎 *Байланыс:*
{links}

/help — командалар тізімі
"""
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=support_menu_markup(),
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        links = _support_contact_block_markdown()
        help_text = f"""
📚 *Көмек · Forecast AI*

🛟 *Қолдау (адам оператор)*
/start немесе /support — *Отзыв / Запрос* түймелері

📎 *Байланыс:*
{links}

---

📊 *Өнім командалары (болжам және аналитика)*
• /forecast `<өнім>` — сұраныс болжамы (мысал: `/forecast iPhone 15`)
• /price `<өнім>` `<қала>` — баға бағыты (мысал: `/price Samsung Galaxy Алматы`)
• /report — қысқа күнделікті есеп
• /alerts — stockout/баға ескертулеріне жазылу
• /cities — қалалар тізімі (баға командасына көмек)
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def forecast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /forecast command"""
        if not context.args:
            await update.message.reply_text(
                "❌ Өнім атауын жазыңыз.\n\n"
                "Мысал: `/forecast iPhone 15`",
                parse_mode='Markdown'
            )
            return

        product_name = " ".join(context.args)

        # Send typing indicator
        await update.message.chat.send_action("typing")

        try:
            # Import here to avoid circular imports
            from services.ai_chat_service import AIChatService

            chat_service = AIChatService()
            response = await chat_service.process_message(
                f"Дай прогноз спроса на {product_name} на 7 дней",
                user_id=str(update.effective_user.id)
            )

            reply_text = f"""
📊 *Болжам: {product_name}*

{response.get('reply', 'Болжам табылмады')}

🔄 Жаңарту: /forecast {product_name}
"""
            await update.message.reply_text(reply_text, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Forecast error: {e}")
            await update.message.reply_text(
                f"⚠️ Қате болды. Қайта көріңіз.\n\nӨнім: {product_name}"
            )

    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /price command"""
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Өнім және қала атауын жазыңыз.\n\n"
                "Мысал: `/price iPhone Almaty`",
                parse_mode='Markdown'
            )
            return

        # Last word is city, rest is product
        city = context.args[-1]
        product_name = " ".join(context.args[:-1])

        await update.message.chat.send_action("typing")

        try:
            from services.ai_chat_service import AIChatService

            chat_service = AIChatService()
            response = await chat_service.process_message(
                f"Анализ цены {product_name} в городе {city}",
                user_id=str(update.effective_user.id)
            )

            reply_text = f"""
💰 *Баға анализі*

📦 Өнім: {product_name}
📍 Қала: {city}

{response.get('reply', 'Ақпарат табылмады')}
"""
            await update.message.reply_text(reply_text, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Price error: {e}")
            await update.message.reply_text("⚠️ Қате болды. Қайта көріңіз.")

    async def alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command - toggle alerts"""
        chat_id = update.effective_chat.id

        keyboard = [
            [
                InlineKeyboardButton("✅ Қосу", callback_data="alerts_on"),
                InlineKeyboardButton("❌ Өшіру", callback_data="alerts_off"),
            ],
            [
                InlineKeyboardButton("📋 Статус", callback_data="alerts_status"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        status = "✅ Қосулы" if chat_id in alert_subscribers else "❌ Өшірулі"

        await update.message.reply_text(
            f"🔔 *Алерттер*\n\nҚазіргі статус: {status}\n\nТаңдаңыз:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def alerts_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle alert button callbacks"""
        query = update.callback_query
        await query.answer()

        chat_id = update.effective_chat.id

        if query.data == "alerts_on":
            alert_subscribers.add(chat_id)
            await query.edit_message_text(
                "✅ *Алерттер қосылды!*\n\n"
                "Сіз келесі хабарламаларды аласыз:\n"
                "• 📉 Stockout ескертулері\n"
                "• 📈 Баға өзгерістері\n"
                "• 🔥 Trending өнімдер",
                parse_mode='Markdown'
            )
        elif query.data == "alerts_off":
            alert_subscribers.discard(chat_id)
            await query.edit_message_text(
                "❌ *Алерттер өшірілді*\n\n"
                "Қайта қосу: /alerts",
                parse_mode='Markdown'
            )
        elif query.data == "alerts_status":
            count = len(alert_subscribers)
            status = "✅ Қосулы" if chat_id in alert_subscribers else "❌ Өшірулі"
            await query.edit_message_text(
                f"📊 *Алерт статусы*\n\n"
                f"Сіздің статус: {status}\n"
                f"Барлық жазылушылар: {count}",
                parse_mode='Markdown'
            )

    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /report command"""
        await update.message.chat.send_action("typing")

        try:
            from services.ai_chat_service import AIChatService

            chat_service = AIChatService()
            response = await chat_service.process_message(
                "Дай краткий отчет: топ продукты, тренды, алерты",
                user_id=str(update.effective_user.id)
            )

            reply_text = f"""
📋 *Күнделікті есеп*
📅 {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}

{response.get('reply', 'Есеп жасалмады')}

🔄 Жаңарту: /report
"""
            await update.message.reply_text(reply_text, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Report error: {e}")
            await update.message.reply_text("⚠️ Есеп жасау қатесі.")

    async def cities_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cities command"""
        cities_text = """
🏙️ *Қазақстан қалалары*

*Tier 1 (Мегаполистер):*
• Алматы - 2.1M тұрғын
• Астана - 1.4M тұрғын

*Tier 2 (Ірі қалалар):*
• Шымкент - 1.1M
• Қарағанды - 500K
• Ақтөбе - 400K
• Тараз - 350K
• Павлодар - 330K

*Tier 3 (Орта қалалар):*
• Өскемен, Семей, Атырау, Қостанай, Петропавл, Орал, Түркістан, Ақтау

💡 Баға сұрау: `/price iPhone Almaty`
"""
        await update.message.reply_text(cities_text, parse_mode='Markdown')

    async def support_type_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отзыв / Запрос таңдалған соң келесі хабарламаны операторға өткізу режимі."""
        query = update.callback_query
        if not query:
            return
        await query.answer()
        data = query.data or ""
        if data == "support:feedback":
            kind = "feedback"
            label = "Отзыв"
        elif data == "support:request":
            kind = "request"
            label = "Запрос"
        else:
            return
        context.user_data["support_awaiting_message"] = True
        context.user_data["support_kind"] = kind
        await query.message.reply_text(
            f"✅ Таңдалды: *{label}*.\n\n"
            "Енді мәселеңізді бір хабарламада жіберіңіз (мәтін, скрин немесе файл).",
            parse_mode="Markdown",
        )

    async def _relay_ticket_to_staff(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        gid = _support_group_id()
        if gid is None:
            await update.message.reply_text(
                "Қолдау топы әлі бапталмаған (`TELEGRAM_SUPPORT_GROUP_ID`). Әкімшіге хабарласыңыз."
            )
            context.user_data.pop("support_awaiting_message", None)
            context.user_data.pop("support_kind", None)
            return

        u = update.effective_user
        username = f"@{u.username}" if u.username else "жоқ"
        kind = context.user_data.get("support_kind", "request")
        kind_label = "Отзыв" if kind == "feedback" else "Запрос"

        header_lines = [
            f"🛟 <b>{html.escape(kind_label)}</b>",
            f"👤 {html.escape((u.full_name or '').strip() or 'User')} ({html.escape(username)})",
            f"🆔 <code>{u.id}</code>",
            "─────────────",
            "<i>Оператор: жауап үшін осы хабарламаға reply.</i>",
        ]
        header = "\n".join(header_lines)
        msg = update.message

        try:
            bridge_id: int
            if msg.photo:
                cap = (msg.caption or "").strip()
                body = f"\n\n{html.escape(cap)}" if cap else ""
                caption = header + body
                if len(caption) > 1024:
                    caption = caption[:1021] + "..."
                sent = await context.bot.send_photo(
                    chat_id=gid,
                    photo=msg.photo[-1].file_id,
                    caption=caption,
                    parse_mode="HTML",
                )
                bridge_id = sent.message_id
            elif msg.text:
                full = header + "\n\n" + html.escape(msg.text)
                if len(full) > 4096:
                    full = full[:4090] + "..."
                sent = await context.bot.send_message(chat_id=gid, text=full, parse_mode="HTML")
                bridge_id = sent.message_id
            else:
                hdr = await context.bot.send_message(
                    chat_id=gid,
                    text=header + "\n\n<i>Қосымша хабарлама төменде.</i>",
                    parse_mode="HTML",
                )
                bridge_id = hdr.message_id
                await context.bot.copy_message(
                    chat_id=gid,
                    from_chat_id=msg.chat_id,
                    message_id=msg.message_id,
                )

            _ticket_bridge[bridge_id] = msg.chat_id
            await msg.reply_text("✅ Жіберілді. Оператор жақында осы чатта жауап береді.")
        except Exception as e:
            logger.exception("Support relay failed: %s", e)
            await msg.reply_text("⚠️ Жіберу сәтсіз. Кейінірек қайта көріңіз.")

        context.user_data.pop("support_awaiting_message", None)
        context.user_data.pop("support_kind", None)

    async def handle_staff_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Қолдау топында тикет хабарламасына reply — қолданушыға қайта жіберу."""
        msg = update.effective_message
        if not msg or not msg.reply_to_message:
            return

        gid = _support_group_id()
        if gid is None or update.effective_chat.id != gid:
            return

        reply_to = msg.reply_to_message
        bot_me = await context.bot.get_me()
        if reply_to.from_user.id != bot_me.id:
            return

        user_chat = _ticket_bridge.get(reply_to.message_id)
        if user_chat is None:
            return

        op_id = update.effective_user.id
        if op_id == bot_me.id:
            return
        if not _is_operator(op_id):
            logger.info("Ignoring staff reply from non-operator telegram user_id=%s", op_id)
            return

        try:
            await context.bot.copy_message(
                chat_id=user_chat,
                from_chat_id=gid,
                message_id=msg.message_id,
            )
        except Exception as e:
            logger.exception("Failed to copy operator reply to user: %s", e)

    async def handle_private_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Жеке чат: қолдау тикеті немесе түймелерге бағыттау (AI жоқ)."""
        if update.effective_chat.type != ChatType.PRIVATE:
            return

        if context.user_data.get("support_awaiting_message"):
            await self._relay_ticket_to_staff(update, context)
            return

        await update.message.reply_text(
            "Қолдау үшін алдымен *Отзыв* немесе *Запрос* таңдаңыз, содан кейін мәселеңізді жіберіңіз.\n\n"
            "Болжам үшін: `/help`",
            parse_mode="Markdown",
            reply_markup=support_menu_markup(),
        )

    def setup_handlers(self, application: Application):
        """Setup all command handlers"""
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("support", self.support_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("forecast", self.forecast_command))
        application.add_handler(CommandHandler("price", self.price_command))
        application.add_handler(CommandHandler("alerts", self.alerts_command))
        application.add_handler(CommandHandler("report", self.report_command))
        application.add_handler(CommandHandler("cities", self.cities_command))

        # Callback handlers for inline buttons
        application.add_handler(CallbackQueryHandler(self.support_type_callback, pattern=r"^support:"))
        application.add_handler(CallbackQueryHandler(self.alerts_callback, pattern="^alerts_"))

        # Operator replies in support group (before private handler)
        sgid = _support_group_id()
        if sgid is not None:
            application.add_handler(MessageHandler(filters.Chat(chat_id=sgid), self.handle_staff_reply))

        # Private chat: human support relay only (no free-text AI)
        application.add_handler(
            MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, self.handle_private_message)
        )

    async def send_alert(self, message: str):
        """Send alert to all subscribers"""
        if not self.application:
            logger.warning("Bot not initialized, cannot send alerts")
            return

        for chat_id in alert_subscribers:
            try:
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to send alert to {chat_id}: {e}")

    async def send_stockout_alert(self, product_name: str, days_until_stockout: int):
        """Send stockout alert"""
        emoji = "🚨" if days_until_stockout <= 2 else "⚠️"
        message = f"""
{emoji} *Stockout Alert!*

📦 Өнім: {product_name}
⏰ Қор таусылуына: {days_until_stockout} күн

Тапсырыс беру керек!
"""
        await self.send_alert(message)

    async def send_price_alert(self, product_name: str, old_price: float, new_price: float):
        """Send price change alert"""
        change = ((new_price - old_price) / old_price) * 100
        emoji = "📈" if change > 0 else "📉"

        message = f"""
{emoji} *Баға өзгерді!*

📦 Өнім: {product_name}
💰 Бұрынғы: ${old_price:.2f}
💰 Жаңа: ${new_price:.2f}
📊 Өзгеріс: {change:+.1f}%
"""
        await self.send_alert(message)


# Global bot instance
telegram_bot = TelegramBotService()


def get_telegram_bot() -> TelegramBotService:
    """Get the global telegram bot instance"""
    return telegram_bot


async def init_telegram_bot():
    """Initialize and start the telegram bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, bot disabled")
        return None

    if _support_group_id() is None:
        logger.warning(
            "TELEGRAM_SUPPORT_GROUP_ID not set — Отзыв/Запрос tickets will not reach operators until configured."
        )

    try:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        telegram_bot.application = application
        telegram_bot.setup_handlers(application)

        # Start polling in background
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)

        telegram_bot.is_running = True
        logger.info("Telegram bot started successfully")

        return application

    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")
        return None


async def stop_telegram_bot():
    """Stop the telegram bot"""
    if telegram_bot.application and telegram_bot.is_running:
        await telegram_bot.application.updater.stop()
        await telegram_bot.application.stop()
        await telegram_bot.application.shutdown()
        telegram_bot.is_running = False
        logger.info("Telegram bot stopped")
