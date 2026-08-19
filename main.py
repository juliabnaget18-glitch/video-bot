import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def handle_ping(request):
    return web.Response(text="Bot is live!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

async def download_via_cobalt(url: str):
    # Օգտագործում ենք պաշտոնական կայուն API-ն
    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    payload = {
        "url": url,
        "vCodec": "h264"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("status") in ["redirect", "stream"]:
                    return data.get("url")
                elif data.get("status") == "error":
                    raise Exception(data.get("error", {}).get("code", "Անհայտ սխալ"))
            raise Exception("API-ն պատասխան չտվեց:")

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Ողջույն 👋 Ուղարկիր ինձ Reels, TikTok, Shorts կամ X-ի հղումը:")

@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    status_msg = await message.answer("⏳ Տեսանյութը մշակվում է...")
    
    try:
        video_url = await download_via_cobalt(message.text)
        await message.answer_video(video=video_url, caption="✨ Ահա ձեր տեսանյութը")
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ Չհաջողվեց ներբեռնել: {str(e)}")

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
