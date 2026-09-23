import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineQueryResultArticle, 
    InputTextMessageContent, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    InlineQueryResultsButton,  # <-- Добавили эту строчку
    WebAppInfo
)

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL", "https://liferidelife.onrender.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.inline_query()
async def inline_query_handler(query: types.InlineQuery):
    try:
        user_query = query.query.strip().lower()

        # Динамическое определение раздела по запросу пользователя
        if any(w in user_query for w in ["кит", "kit", "фрейм", "апгрейд"]):
            btn_text = "⚡ Открыть Upgrade Kits"
            param = "upgrade_kits"
        elif any(w in user_query for w in ["компонент", "запчаст", "колес", "групсет", "руль"]):
            btn_text = "⚙️ Открыть Комплектующие"
            param = "components"
        elif any(w in user_query for w in ["полезн", "гайд", "ростовк", "база"]):
            btn_text = "💡 Открыть Базу знаний"
            param = "guides"
        elif any(w in user_query for w in ["отзыв", "заказ"]):
            btn_text = "⭐️ Читать Отзывы"
            param = "reviews"
        else:
            # Вариант по умолчанию (если ввели просто @liferidelife_bot)
            btn_text = "🚲 Открыть подбор и каталог велосипедов"
            param = "bikes"

        # Передаем пустой список результатов (results=[]), чтобы исключить отправку сообщений в группы.
        # Единственное действие — нажатие на плашку перехода в ЛС.
        await query.answer(
            results=[],
            cache_time=0,
            is_personal=True,
            button=InlineQueryResultsButton(
                text=btn_text,
                start_parameter=param
            )
        )
    except Exception as e:
        print(f"[ERROR] Inline query crash: {e}")
        await query.answer([], cache_time=1, is_personal=True)

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    print(f"Webhook установлен на: {WEBHOOK_URL}")

def main():
    dp.startup.register(on_startup)
    app = web.Application()
    
    # 1. Добавляем простой healthcheck для UptimeRobot
    async def healthcheck(request):
        return web.Response(text="Bot is alive!", status=200)
    
    app.router.add_get("/", healthcheck)

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
