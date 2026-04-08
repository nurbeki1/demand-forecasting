"""
Telegram Bot Service for Demand Forecasting
Provides instant forecasts, alerts, and reports via Telegram
"""

import os
import logging
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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


class TelegramBotService:
    """Telegram Bot Service for demand forecasting interactions"""

    def __init__(self):
        self.application: Optional[Application] = None
        self.is_running = False

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat_id = update.effective_chat.id

        # Store user
        user_chat_ids[str(user.id)] = chat_id

        welcome_message = f"""
🤖 *Сәлем, {user.first_name}!*

Мен Demand Forecasting AI ботымын. Сізге көмектесе аламын:

📊 *Командалар:*
/forecast `<product>` - Болжам алу
/price `<product>` `<city>` - Баға сұрау
/alerts - Алерттерді қосу/өшіру
/report - Күнделікті есеп
/cities - Қалалар тізімі
/help - Көмек

💡 *Мысал:*
`/forecast iPhone 15`
`/price Samsung Galaxy Almaty`

Сұрағыңызды жазыңыз! 👇
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📚 *Көмек*

*Негізгі командалар:*
• /forecast `<product>` - Өнім болжамын алу
• /price `<product>` `<city>` - Қала бойынша баға
• /alerts - Алерттер қосу/өшіру
• /report - Күнделікті есеп алу
• /cities - Қолжетімді қалалар
• /categories - Категориялар тізімі
• /trending - Трендтегі өнімдер

*Мысалдар:*
• `/forecast iPhone 15 Pro`
• `/price Samsung Galaxy S24 Астана`
• `/trending electronics`

*Сұрақтар:*
Кез келген сұрақты жай жазыңыз:
• "iPhone қанша тұрады?"
• "Алматыда ең көп сатылатын телефон?"
• "Келесі аптаға болжам бер"
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

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle free text messages"""
        text = update.message.text

        await update.message.chat.send_action("typing")

        try:
            from services.ai_chat_service import AIChatService

            chat_service = AIChatService()
            response = await chat_service.process_message(
                text,
                user_id=str(update.effective_user.id)
            )

            reply = response.get('reply', 'Кешіріңіз, түсінбедім. /help командасын қолданыңыз.')

            # Truncate if too long for Telegram
            if len(reply) > 4000:
                reply = reply[:4000] + "\n\n... (қысқартылды)"

            await update.message.reply_text(reply, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Message handling error: {e}")
            await update.message.reply_text(
                "⚠️ Қате болды. Қайта көріңіз немесе /help командасын қолданыңыз."
            )

    def setup_handlers(self, application: Application):
        """Setup all command handlers"""
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("forecast", self.forecast_command))
        application.add_handler(CommandHandler("price", self.price_command))
        application.add_handler(CommandHandler("alerts", self.alerts_command))
        application.add_handler(CommandHandler("report", self.report_command))
        application.add_handler(CommandHandler("cities", self.cities_command))

        # Callback handlers for inline buttons
        application.add_handler(CallbackQueryHandler(self.alerts_callback, pattern="^alerts_"))

        # Message handler for free text (must be last)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

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
