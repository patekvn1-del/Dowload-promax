import os

TOKEN = os.environ.get("BOT_TOKEN")

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

    await query.edit_message_text("Downloading...")

    if data == "video":

        ydl_opts = {
            "format": "best",
            "outtmpl": "video.%(ext)s"
        }

    elif data == "mp3":

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "music.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3"
            }]
        }

    elif data == "thumb":

        ydl_opts = {
            "skip_download": True
        }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            if data == "thumb":
                await query.message.reply_photo(info["thumbnail"])
                return

            file = ydl.prepare_filename(info)

        if data == "mp3":
            await query.message.reply_audio(audio=open(file,"rb"))
        else:
            await query.message.reply_video(video=open(file,"rb"))

    except:
        await query.message.reply_text("Download lỗi")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
