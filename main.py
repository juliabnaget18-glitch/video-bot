import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiohttp import web
import yt_dlp

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def handle_ping(request):
    return web.Response(text="Bot is running!")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()


def download_media(url: str, output_path: str):
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_path,
        "quiet": True,
        "no_warnings": True,
        # TikTok-ի ու Instagram-ի համար հատուկ Header-ներ
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Ողջույն 👋 Ուղարկիր ինձ Reels, TikTok, Shorts կամ X-ի հղումը, և ես այն կներբեռնեմ:"
    )


@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    status_msg = await message.answer("⏳ Տեսանյութը մշակվում է, սպասեք...")
    file_path = f"video_{message.from_user.id}.mp4"

    try:
        await asyncio.to_thread(download_media, message.text, file_path)

        await message.answer_video(
            video=types.FSInputFile(file_path), caption="✨ Ահա ձեր տեսանյութը"
        )
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(
            f"❌ Չհաջողվեց ներբեռնել: {str(e)[:150]}"
        )  # կարճ սխալի տեքստ

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


async def main():
    await start_web_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
