import asyncio
import os
import httpx
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command

# Token-ը վերցնելու է Render-ի environment variable-ից (անվտանգության համար)
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def get_direct_video_url(media_url: str):
    url = "https://api.cobalt.tools/"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {"url": media_url}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        data = response.json()
        return data.get("url")


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Ողջույն 👋 Ուղարկիր ինձ Reels, TikTok, Shorts կամ X-ի հղումը, և եu այն կներբեռնեմ:"
    )


@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    status_msg = await message.answer("⏳ Մշակվում է, սպասեք...")

    try:
        video_url = await get_direct_video_url(message.text)

        if video_url:
            await message.answer_video(video=video_url, caption="✨ Ահա տեսանյութը")
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Չհաջողվեց ստանալ տեսանյութի հղումը:")

    except Exception:
        await status_msg.edit_text("❌ Սխալ տեղի ունեցավ, փորձեք մեկ այլ հղում:")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
