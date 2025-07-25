import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("video_trim_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply_text("👋 Hello I am Haklesh Bot.\nSend me a video and I'll remove the first 4 seconds.")

@app.on_message(filters.video)
async def trim_4sec(client, message):
    try:
        sent = await message.reply_text("📥 Downloading video...")
        downloaded = await message.download(file_name="input.mp4")
        await sent.edit("✂️ Trimming first 4 seconds...")

        output = "trimmed.mp4"
        cmd = f'ffmpeg -ss 4 -i "{downloaded}" -c copy "{output}" -y'
        subprocess.run(cmd, shell=True)

        await sent.edit("📤 Uploading trimmed video...")
        await message.reply_video(video=output, caption="✅ Trimmed 4 seconds from start")

        os.remove(downloaded)
        os.remove(output)
        await sent.delete()

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

app.run()
