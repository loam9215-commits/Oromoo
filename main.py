import os
import logging
from typing import List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from deep_translator import GoogleTranslator
from flask import Flask

# Flask app for health checks (required for Render)
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Oromo Translator Bot is Running!"

@app.route('/health')
def health():
    return "OK", 200

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable (SECURE)
TOKEN = os.getenv('BOT_TOKEN')

# Channel usernames (without @) - Bot must be admin in these for checks!
CHANNELS = ['B0T5TOR', 't9account']

# Initialize translator for Oromo ('om') - auto-detects source
translator = GoogleTranslator(source='auto', target='om')

# Oromo messages (pre-defined for speed)
OROMO_WELCOME = "Baga nagaan dhufte! 📝 \n\nBarreeffama kamuu naaf ergaa Afaan Oromootti nan hiika"

OROMO_PROMPT = "👋 *Akkam, {user_name}!* 🌟\n\nkanneen kana join gochuu qabda!!"

OROMO_RETRY = "❌ *Hin dabartu, {user_name}!* ❌\n\nKanneen kana join gochuu qabda🌟"

OROMO_REJOIN = "❌ *Kanneen kana join gochuu qabda!!"

OROMO_SUPPORT = "@Pabloecov support ergaa. Message ergaa fi malee ergaa! 📞"

OROMO_ERROR = "😔 *Rakkoon dhufe, irra deebi'ii yaali!*"

OROMO_GREETING = "Akkami?"

OROMO_LANGUAGES = "Afaan 100+ kanneen naaf ergaa nan hiika: English, Amharic, Arabic, French, Spanish, etc. /help ergaa!"

async def check_membership(bot, user_id: int, channels: List[str]) -> bool:
    """Check if user is member of all required channels."""
    for channel in channels:
        try:
            chat_id = f'@{channel}'
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            logger.error(f"Membership check error for {channel}: {e}")
            return False  # Fail safe
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start - Channel check first."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"

    if await check_membership(context.bot, user_id, CHANNELS):
        await update.message.reply_text(OROMO_WELCOME, parse_mode='Markdown')
    else:
        keyboard = [
            [
                InlineKeyboardButton("📢 @B0T5TOR", url='https://t.me/B0T5TOR'),
                InlineKeyboardButton("📢 @t9account", url='https://t.me/t9account')
            ],
            [InlineKeyboardButton("✅ Joined!", callback_data='check_joined')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        prompt_text = OROMO_PROMPT.format(user_name=user_name)
        await update.message.reply_text(prompt_text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle join check button."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_name = query.from_user.first_name or "User"

    if query.data == 'check_joined':
        if await check_membership(context.bot, user_id, CHANNELS):
            await query.edit_message_text(OROMO_WELCOME, parse_mode='Markdown')
        else:
            keyboard = [
                [
                    InlineKeyboardButton("📢 @B0T5TOR", url='https://t.me/B0T5TOR'),
                    InlineKeyboardButton("📢 @t9account", url='https://t.me/t9account')
                ],
                [InlineKeyboardButton("✅ Joined!", callback_data='check_joined')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            retry_text = OROMO_RETRY.format(user_name=user_name)
            await query.edit_message_text(retry_text, reply_markup=reply_markup, parse_mode='Markdown')

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /support - Direct to @Pabloecov."""
    user_id = update.effective_user.id

    if not await check_membership(context.bot, user_id, CHANNELS):
        keyboard = [
            [
                InlineKeyboardButton("📢 @B0T5TOR", url='https://t.me/B0T5TOR'),
                InlineKeyboardButton("📢 @t9account", url='https://t.me/t9account')
            ],
            [InlineKeyboardButton("✅ Joined!", callback_data='check_joined')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(OROMO_REJOIN, reply_markup=reply_markup, parse_mode='Markdown')
        return

    await update.message.reply_text(OROMO_SUPPORT, parse_mode='Markdown')

async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /languages - List supported languages."""
    user_id = update.effective_user.id

    if not await check_membership(context.bot, user_id, CHANNELS):
        keyboard = [
            [
                InlineKeyboardButton("📢 @B0T5TOR", url='https://t.me/B0T5TOR'),
                InlineKeyboardButton("📢 @t9account", url='https://t.me/t9account')
            ],
            [InlineKeyboardButton("✅ Joined!", callback_data='check_joined')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(OROMO_REJOIN, reply_markup=reply_markup, parse_mode='Markdown')
        return

    await update.message.reply_text(OROMO_LANGUAGES, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help - More features overview."""
    user_id = update.effective_user.id

    if not await check_membership(context.bot, user_id, CHANNELS):
        keyboard = [
            [
                InlineKeyboardButton("📢 @B0T5TOR", url='https://t.me/B0T5TOR'),
                InlineKeyboardButton("📢 @t9account", url='https://t.me/t9account')
            ],
            [InlineKeyboardButton("✅ Joined!", callback_data='check_joined')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(OROMO_REJOIN, reply_markup=reply_markup, parse_mode='Markdown')
        return

    try:
        help_text = translator.translate(
            "• /start - Start bot\n• /support - Contact @Pabloecov\n• /languages - Supported languages\n• Send any text - I translate to Oromo\n\nYou can add me to groups!"
        )
    except Exception as e:
        help_text = "• /start - Ergaa\n• /support - @Pabloecov ergaa\n• /languages - Afaan kanneen\n• Barreeffama ergaa - Afaan Oromootti nan hiika\n\nGroupoota keessatti add gochuu!"
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Translate messages to Oromo - Pure translation only."""
    user_id = update.effective_user.id
    text = update.message.text

    if not text:
        return

    text_lower = text.lower().strip()

    if not await check_membership(context.bot, user_id, CHANNELS):
        keyboard = [
            [
                InlineKeyboardButton("📢 @B0T5TOR", url='https://t.me/B0T5TOR'),
                InlineKeyboardButton("📢 @t9account", url='https://t.me/t9account')
            ],
            [InlineKeyboardButton("✅ Joined!", callback_data='check_joined')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(OROMO_REJOIN, reply_markup=reply_markup, parse_mode='Markdown')
        return

    # Skip commands
    if text_lower.startswith('/'):
        return

    # Special greeting case
    if text_lower in ['hi', 'hello', 'hey', 'hola']:
        await update.message.reply_text(OROMO_GREETING)
        return

    try:
        # Translate and respond with pure Oromo
        translation = translator.translate(text)
        await update.message.reply_text(translation)
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text(OROMO_ERROR)

def run_flask():
    """Run Flask server for health checks."""
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)

def main() -> None:
    """Run the bot."""
    # Check if token is available
    if not TOKEN:
        logger.error("❌ BOT_TOKEN environment variable not found!")
        logger.error("Please set BOT_TOKEN in Render environment variables")
        return

    # Start Flask in background thread for health checks
    from threading import Thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Create bot application
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("languages", languages_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))

    logger.info("🤖 Oromo Translator Bot Starting...")
    logger.info("Channels: @B0T5TOR, @t9account | Support: @Pabloecov")
    
    # Start polling
    application.run_polling()

if __name__ == '__main__':
    main()
