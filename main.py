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

# Dictionary to avoid message edit duplicates
last_update = {}

# /start command
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply_text(
        "👋 Hello I am Haklesh Bot.\n\n"
        "🎬 Send me a video and I will:\n"
        "➤ Show download progress\n"
        "➤ Trim first 4 seconds\n"
        "➤ Send back cleaned video\n\n"
        "✅ Powered by @tg_mr_x8"
    )


# Download progress tracker
async def progress(current, total, message: Message, start_time):
    chat_id = message.chat.id
    percent = int(current * 100 / total)

    # Don't update same percentage again
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


# Main video handler
@app.on_message(filters.video & filters.private)
async def process_video(client, message: Message):
    try:
        status = await message.reply_text("📥 Starting download...")
        start = time.time()

        input_path = await message.download(
            file_name="input.mp4",
            progress=progress,
            progress_args=(status, start)
        )

        await status.edit("✂️ Trimming first 4 seconds...")

        output_path = "trimmed.mp4"
        cmd = f'ffmpeg -ss 4 -i "{input_path}" -c copy "{output_path}" -y'
        subprocess.run(cmd, shell=True)

        await status.edit("✅ Trimming done!\n📤 Uploading trimmed video...")

        await message.reply_video(video=output_path, caption="✅ Trimmed first 4 seconds successfully!")
        await status.delete()

        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

app.run()
