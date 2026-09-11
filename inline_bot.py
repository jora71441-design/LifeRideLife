import os
import json
import html
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, 'products.json')

def get_products():
    try:
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("products") or data.get("items") or list(data.values())
        else:
            print(f"[ERROR] Файл не найден: {JSON_PATH}")
    except Exception as e:
        print(f"[ERROR] Ошибка чтения JSON: {e}")
    return []

@dp.inline_query()
async def inline_query_handler(query: types.InlineQuery):
    user_text = query.query.strip().lower()
    results = []
    
    try:
        products = get_products()

        for idx, item in enumerate(products):
            if not isinstance(item, dict):
                continue

            raw_title = str(item.get("title") or item.get("name") or f"Товар #{idx+1}")
            raw_desc = str(item.get("description") or item.get("text") or item.get("size") or "")
            raw_price = str(item.get("price") or "")
            link = str(item.get("link") or item.get("url") or "https://t.me/liferidelife_bot")

            search_content = f"{raw_title} {raw_desc} {raw_price}".lower()

            if user_text and user_text not in search_content:
                continue

            # Безопасное экранирование HTML-тегов из объявлений
            safe_title = html.escape(raw_title)
            safe_desc = html.escape(raw_desc)
            safe_price = html.escape(raw_price)

            caption = f"<b>{safe_title}</b>\n"
            if safe_price: 
                caption += f"💰 <b>Цена:</b> {safe_price}\n"
            if safe_desc: 
                caption += f"\n{safe_desc}\n"

            results.append(
                InlineQueryResultArticle(
                    id=str(item.get("id", idx)),
                    title=f"{raw_title} {f'| {raw_price}' if raw_price else ''}",
                    description=raw_desc[:60] if raw_desc else "Нажмите для отправки",
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
    except Exception as e:
        print(f"[ERROR] Inline query crash: {e}")
        await query.answer([], cache_time=1, is_personal=False)

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
