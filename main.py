import os
import time
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("video_trim_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

last_update = {}

# /start command
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply_text(
        "👋 Hello I am Haklesh Bot.\n\n"
        "🎬 Send a video and I will:\n"
        "➤ Trim first 4 seconds\n"
        "➤ Keep original caption\n"
        "➤ Upload with proper thumbnail\n\n"
        "✅ Powered by @tg_mr_x8"
    )

# Progress function
async def progress(current, total, message: Message, start_time):
    chat_id = message.chat.id
    percent = int(current * 100 / total)
    if last_update.get(chat_id) == percent:
        return
    last_update[chat_id] = percent
    speed = current / (time.time() - start_time)
    try:
        await message.edit_text(
            f"📥 Downloading...\n"
            f"{percent}% complete\n"
            f"💾 {current / 1024 / 1024:.2f} MB of {total / 1024 / 1024:.2f} MB\n"
            f"⚡ Speed: {speed / 1024:.2f} KB/s"
        )
    except:
        pass

# Main handler
@app.on_message(filters.video & filters.private)
async def process_video(client, message: Message):
    try:
        status = await message.reply_text("📥 Downloading video...")
        start = time.time()

        input_path = await message.download(
            file_name="input.mp4",
            progress=progress,
            progress_args=(status, start)
        )

        await status.edit("✂️ Trimming first 4 seconds...")

        output_path = os.path.abspath("trimmed.mp4")
        trim_cmd = f'ffmpeg -ss 4 -i "{input_path}" -c copy "{output_path}" -y -loglevel error'
        result = subprocess.run(trim_cmd, shell=True)

        if not os.path.exists(output_path):
            await message.reply_text("❌ Error: Trimming failed. No output file found.")
            return

        await status.edit("📸 Creating thumbnail...")

        thumb_path = os.path.abspath("thumb.jpg")
        thumb_cmd = f'ffmpeg -ss 1 -i "{output_path}" -vframes 1 -q:v 2 "{thumb_path}" -y -loglevel error'
        subprocess.run(thumb_cmd, shell=True)

        if not os.path.exists(thumb_path):
            await message.reply_text("❌ Error: Thumbnail not created.")
            return

        await status.edit("📤 Uploading trimmed video...")

        await message.reply_video(
            video=output_path,
            thumb=thumb_path,
            caption=message.caption or "✅ Trimmed 4 seconds.",
            supports_streaming=True
        )

        await status.delete()

        os.remove(input_path)
        os.remove(output_path)
        os.remove(thumb_path)

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

app.run()
