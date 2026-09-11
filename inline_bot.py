import os
import json
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Гарантированный абсолютный путь к products.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, 'products.json')

def get_products():
    try:
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Поддержка как простого массива [...], так и словарей вида {"items": [...]}
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("products") or data.get("items") or list(data.values())
        else:
            print(f"Файл {JSON_PATH} не найден!")
    except Exception as e:
        print(f"Ошибка чтения JSON: {e}")
    return []

@dp.inline_query()
async def inline_query_handler(query: types.InlineQuery):
    user_text = query.query.strip().lower()
    products = get_products()

    results = []
    for idx, item in enumerate(products):
        if not isinstance(item, dict):
            continue

        title = str(item.get("title") or item.get("name") or f"Товар #{idx+1}")
        desc = str(item.get("description") or item.get("text") or item.get("size") or "")
        price = str(item.get("price") or "")
        link = str(item.get("link") or item.get("url") or "https://t.me/liferidelife_bot")

        search_content = f"{title} {desc} {price}".lower()

        # Фильтрация (если текст пустой — показывает все товары)
        if user_text and user_text not in search_content:
            continue

        # Безопасный HTML вместо Markdown (не ломается от спецсимволов)
        caption = f"<b>{title}</b>\n"
        if price: 
            caption += f"💰 <b>Цена:</b> {price}\n"
        if desc: 
            caption += f"\n{desc}\n"

        results.append(
            InlineQueryResultArticle(
                id=str(item.get("id", idx)),
                title=f"{title} {f'| {price}' if price else ''}",
                description=desc[:60] if desc else "Нажмите для отправки",
                input_message_content=InputTextMessageContent(
                    message_text=caption,
                    parse_mode="HTML"
                ),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🚴‍♂️ Открыть в Mini App", url="https://t.me/liferidelife_bot/app")
                ]])
            )
        )
        if len(results) >= 20:
            break

    await query.answer(results, cache_time=1, is_personal=False)

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
