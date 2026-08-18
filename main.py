import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
import yt_dlp

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def download_media(url: str, output_path: str):
    """Ներբեռնում է տեսանյութը yt-dlp-ով"""
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_path,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Ողջույն 👋 Ուղարկիր ինձ Reels, TikTok, Shorts կամ X-ի հղումը, և եu այն կներբեռնեմ:"
    )


@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    status_msg = await message.answer("⏳ Տեսանյութը մշակվում է, սպասեք...")
    file_path = f"video_{message.from_user.id}.mp4"

    try:
        # Ներբեռնում ենք yt-dlp-ով ֆոնում
        await asyncio.to_thread(download_media, message.text, file_path)

        # Ուղարկում ենք Telegram-ում
        await message.answer_video(
            video=types.FSInputFile(file_path), caption="✨ Ահա ձեր տեսանյութը"
        )
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Չհաջողվեց ներբեռնել: {str(e)}")

    finally:
        # Ջնջում ենք ֆայլը սերվերից, որ տեղ չզբաղեցնի
        if os.path.exists(file_path):
            os.remove(file_path)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
