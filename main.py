import os
import time
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ.get("API_ID", "your_api_id"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

app = Client("trim_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

last_update = {}

# START command
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply_text(
        "👋 Hello! I trim first 4 seconds from your video.\n"
        "Send me a video now.\n\n"
        "⚙️ Fast Mode: Enabled\n"
        "📽️ Uploads will include thumbnail and caption.\n"
        "🔗 Powered by @tg_mr_x8"
    )

# Progress updater
async def progress(current, total, message: Message, start_time):
    chat_id = message.chat.id
    percent = int(current * 100 / total)
    if last_update.get(chat_id) == percent:
        return
    last_update[chat_id] = percent
    speed = current / (time.time() - start_time)
    try:
        await message.edit_text(
            f"📥 Downloading: {percent}%\n"
            f"⚡ Speed: {speed / 1024:.2f} KB/s"
        )
    except:
        pass

# Video handler
@app.on_message(filters.video & filters.private)
async def handle_video(client, message: Message):
    try:
        status = await message.reply_text("📥 Downloading...")
        start = time.time()

        # Ensure folder
        os.makedirs("downloads", exist_ok=True)

        # Download video
        input_path = await message.download(
            file_name="downloads/input.mp4",
            block_size=1024 * 1024,
            progress=progress,
            progress_args=(status, start)
        )

        await status.edit("✂️ Trimming first 4 seconds...")

        # Trim command (re-encoded)
        trimmed_path = os.path.abspath("downloads/trimmed.mp4")
        trim_cmd = (
            f'ffmpeg -ss 4 -i "{input_path}" -t 99999 -preset veryfast '
            f'-c:v libx264 -c:a aac "{trimmed_path}" -y -loglevel error'
        )
        subprocess.run(trim_cmd, shell=True)

        if not os.path.exists(trimmed_path):
            return await status.edit("❌ Error: Trimming failed.")

        # Generate thumbnail
        await status.edit("📸 Creating thumbnail...")
        thumb_path = os.path.abspath("downloads/thumb.jpg")
        thumb_cmd = (
            f'ffmpeg -ss 2 -i "{trimmed_path}" -frames:v 1 -q:v 2 "{thumb_path}" -y -loglevel error'
        )
        subprocess.run(thumb_cmd, shell=True)

        if not os.path.exists(thumb_path):
            return await status.edit("❌ Error: Thumbnail failed.")

        # Upload video
        await status.edit("📤 Uploading trimmed video...")

        await message.reply_video(
            video=trimmed_path,
            thumb=thumb_path,
            caption=message.caption or "✅ Trimmed from 4th second.",
            supports_streaming=True
        )

        await status.delete()

        # Cleanup
        os.remove(input_path)
        os.remove(trimmed_path)
        os.remove(thumb_path)

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

app.run()
