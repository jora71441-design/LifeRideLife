import os
import json
import html
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

TOKEN = os.getenv("BOT_TOKEN")
# Render автоматически создает эту переменную с адресом вашего сервиса
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL", "https://liferidelife.onrender.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

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
        # 1. Если текст пустой — формируем навигационное меню разделами
        if not user_text:
            nav_items = [
                {
                    "id": "nav_bikes",
                    "title": "🔍 Найти свой вел",
                    "desc": "Подбор велосипедов по росту, бренду и бюджету",
                    "text": "🚲 Нажмите ниже, чтобы запустить подбор велосипеда:",
                    "btn_text": "🚲 Открыть подбор велосипедов",
                    "param": "bikes"
                },
                {
                    "id": "nav_kits",
                    "title": "⚡ Upgrade Kits",
                    "desc": "Готовые комплекты для апгрейда и фреймсеты",
                    "text": "⚡ Выберите готовый Upgrade Kit для вашего байка:",
                    "btn_text": "⚡ Перейти к Upgrade Kits",
                    "param": "upgrade_kits"
                },
                {
                    "id": "nav_components",
                    "title": "⚙️ Комплектуха",
                    "desc": "Групсеты, колеса, рули и компоненты",
                    "text": "⚙️ Перейдите в каталог запчастей и комплектующих:",
                    "btn_text": "⚙️ Открыть комплектующие",
                    "param": "components"
                },
                {
                    "id": "nav_useful",
                    "title": "💡 Полезности",
                    "desc": "Гайды по выбору ростовки, обслуживание и таблицы",
                    "text": "💡 Полезная база знаний LifeRideLife:",
                    "btn_text": "💡 Читать полезности",
                    "param": "guides"
                },
                {
                    "id": "nav_reviews",
                    "title": "⭐️ Отзывы",
                    "desc": "Отзывы покупателей и выполненные заказы",
                    "text": "⭐️ Отзывы наших клиентов и истории доставок:",
                    "btn_text": "⭐️ Читать отзывы",
                    "param": "reviews"
                }
            ]

            for nav in nav_items:
                results.append(
                    InlineQueryResultArticle(
                        id=nav["id"],
                        title=nav["title"],
                        description=nav["desc"],
                        input_message_content=InputTextMessageContent(
                            message_text=f"<b>{nav['title']}</b>\n\n{nav['text']}",
                            parse_mode="HTML"
                        ),
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(
                                text=nav["btn_text"], 
                                url=f"https://t.me/liferidelife_bot/app?startapp={nav['param']}"
                            )
                        ]])
                    )
                )

        # 2. Дальше подтягиваем обычный поиск по товарам
        products = get_products()

        for idx, item in enumerate(products):
            if not isinstance(item, dict):
                continue

            raw_title = str(item.get("title") or item.get("name") or f"Товар #{idx+1}")
            raw_desc = str(item.get("description") or item.get("text") or item.get("size") or "")
            raw_price = str(item.get("price") or "")

            search_content = f"{raw_title} {raw_desc} {raw_price}".lower()

            # Если пользователь ввел поисковый запрос (например "sram"), фильтруем
            if user_text and user_text not in search_content:
                continue

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
                        InlineKeyboardButton(
                            text="🚴‍♂️ Открыть в Mini App", 
                            url="https://t.me/liferidelife_bot/app"
                        )
                    ]])
                )
            )
            if len(results) >= 20:
                break

        await query.answer(results, cache_time=1, is_personal=False)
    except Exception as e:
        print(f"[ERROR] Inline query crash: {e}")
        await query.answer([], cache_time=1, is_personal=False)


async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    print(f"Webhook установлен на: {WEBHOOK_URL}")

def main():
    dp.startup.register(on_startup)
    app = web.Application()
    
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
