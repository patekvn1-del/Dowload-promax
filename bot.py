import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "7732409041:AAEZn_TMU_s-kLq_IXIpfZw9xdw2cdjpXHA"

user_links = {}

async def receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_links[update.message.from_user.id] = url

    keyboard = [
        [InlineKeyboardButton("🎬 Video", callback_data="video")],
        [InlineKeyboardButton("🎵 MP3", callback_data="mp3")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")]
    ]

    await update.message.reply_text(
        "Chọn cách tải",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user.id
    url = user_links.get(user)
    data = query.data

    await query.edit_message_text("⏳ Đang tải...")

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        if data == "video":
            ydl_opts = {
                "format": "best[ext=mp4]/best",
                "outtmpl": "/tmp/video.%(ext)s",
                "http_headers": headers
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file = ydl.prepare_filename(info)
            await query.message.reply_video(video=open(file, "rb"))

        elif data == "mp3":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "/tmp/music.%(ext)s",
                "http_headers": headers,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3"
                }]
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file = "/tmp/music.mp3"
            await query.message.reply_audio(audio=open(file, "rb"))

        elif data == "thumb":
            ydl_opts = {
                "skip_download": True,
                "http_headers": headers
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            await query.message.reply_photo(info["thumbnail"])

    except Exception as e:
        await query.message.reply_text(f"❌ Lỗi: {str(e)}")


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
