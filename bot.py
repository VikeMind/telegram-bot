from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp
import os

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me a YouTube, TikTok, Facebook, or Instagram link, and I’ll download it for you.")

# Handle incoming links
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    if any(x in link for x in ["youtube.com", "youtu.be", "facebook.com", "tiktok.com", "instagram.com"]):
        keyboard = [
            [InlineKeyboardButton("🎥 Download Video", callback_data=f"video|{link}")],
            [InlineKeyboardButton("🎵 Download Audio", callback_data=f"audio|{link}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Choose what to download:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("❌ Please send a valid video link from YouTube, TikTok, Facebook, or Instagram.")

# Handle user button choice
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice, link = query.data.split("|")
    await query.edit_message_text(text="⏳ Downloading, please wait...")

    try:
        ydl_opts = {}

        if choice == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
            }

        os.makedirs("downloads", exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            file_path = ydl.prepare_filename(info)
            if choice == "audio":
                file_path = os.path.splitext(file_path)[0] + ".mp3"

        await query.edit_message_text(text="✅ Download complete! Sending file...")
        await context.bot.send_document(chat_id=query.message.chat_id, document=open(file_path, 'rb'))

        os.remove(file_path)

    except Exception as e:
        await query.edit_message_text(text=f"⚠️ Error: {str(e)}")

# Main bot setup
def main():
    TOKEN = "8193403927:AAH7HSDpg83wVNCyGU-iOOd6RAlKeMsOmz0"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

