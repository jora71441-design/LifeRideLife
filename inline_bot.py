import os
import json
import requests
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
PRODUCTS_URL = "https://jora7144-design.github.io/LifeRideLife/products.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.inline_query()
async def inline_query_handler(query: types.InlineQuery):
    user_text = query.query.strip().lower()
    
    try:
        response = requests.get(PRODUCTS_URL, timeout=5)
        products = response.json() if response.status_code == 200 else []
    except Exception:
        products = []

    results = []
    for item in products:
        title = item.get("title", "Товар")
        desc = item.get("description", "")
        price = item.get("price", "")
        link = item.get("link", "https://t.me/liferidelife_bot")
        
        # Фильтрация по поисковому запросу
        if user_text and user_text not in title.lower() and user_text not in desc.lower():
            continue

        results.append(
            InlineQueryResultArticle(
                id=str(item.get("id", len(results))),
                title=title,
                description=f"{price} | {desc[:60]}...",
                input_message_content=InputTextMessageContent(
                    message_text=f"🚴 **{title}**\n💰 Цена: {price}\n\n{desc}\n\n[Посмотреть в канале]({link})",
                    parse_mode="Markdown"
                ),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="Открыть каталог", url="https://t.me/liferidelife_bot/app")
                ]])
            )
        )
        if len(results) >= 20:
            break

    await query.answer(results, cache_time=10, is_personal=False)

# Минимальный сервер для Render
async def handle_ping(request):
    return web.Response(text="Bot is alive!")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
