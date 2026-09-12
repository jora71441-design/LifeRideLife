import os
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

@dp.inline_query()
async def inline_query_handler(query: types.InlineQuery):
    results = []
    
    try:
        # Статичный список из 5 пунктов меню
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
                "text": "💡 Полезная база знаний:",
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

        # Увеличил cache_time до 300 секунд (5 минут). 
        # Так как меню больше не меняется от введенного текста, Telegram закеширует ответ,
        # и меню будет выпадать мгновенно без постоянных запросов к нашему серверу.
        await query.answer(results, cache_time=300, is_personal=False)
        
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
