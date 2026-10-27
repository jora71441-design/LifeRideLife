import os
import time
import urllib.request
import json
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineQueryResultPhoto,
    InlineQueryResultsButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL", "https://liferidelife.onrender.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

PRODUCTS_URL = "https://jora71441-design.github.io/LifeRideLife/products.json"
BASE_IMG_URL = "https://jora71441-design.github.io/LifeRideLife"

# Кэш каталога в памяти, чтобы не нагружать сеть при каждом вводе
_catalog_cache = {"timestamp": 0, "items": {}}

def get_cached_products():
    now = time.time()
    # Обновляем кэш раз в 5 минут
    if now - _catalog_cache["timestamp"] > 300 or not _catalog_cache["items"]:
        try:
            req = urllib.request.Request(
                PRODUCTS_URL,
                headers={"User-Agent": "LifeRideLifeBot/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                _catalog_cache["items"] = {str(item["id"]): item for item in data}
                _catalog_cache["timestamp"] = now
        except Exception as e:
            print(f"[WARN] Не удалось загрузить products.json: {e}")
    return _catalog_cache["items"]


bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.inline_query()
async def inline_query_handler(query: types.InlineQuery):
    q = (query.query or "").strip().lower()

    # 1. Если передали bike_<id> — отдаем карточку конкретного велосипеда
    if q.startswith("bike_"):
        raw_id = q.replace("bike_", "").strip()
        products = get_cached_products()
        bike = products.get(raw_id)

        if bike:
            title = bike.get("title", "Велосипед LifeRideLife")
            price = bike.get("price", "По запросу")
            tags = bike.get("originalTagsText", "")

            img_rel = bike.get("imgUrl", "")
            if img_rel.startswith("./"):
                photo_url = f"{BASE_IMG_URL}/{img_rel[2:]}"
            elif img_rel.startswith("http"):
                photo_url = img_rel
            else:
                photo_url = f"{BASE_IMG_URL}/{img_rel}"

            caption = (
                f"🚴 <b>{title}</b>\n"
                f"💰 <b>{price}</b>\n\n"
                f"{tags}\n\n"
                f"🟢 <i>LifeRideLife • Подбор и сопровождение</i>"
            )

            # Инлайн-кнопка для перехода сразу в Mini App на этот байк
            app_url = f"https://t.me/liferidelife_bot?startapp=bike_{raw_id}"
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(text="🚴‍♂️ Открыть в Life Ride Life", url=app_url)
                ]]
            )

            result_photo = InlineQueryResultPhoto(
                id=f"bike_{raw_id}",
                photo_url=photo_url,
                thumbnail_url=photo_url,
                title=f"{title} ({price})",
                description=f"Отправить карточку байка: {price}",
                caption=caption,
                parse_mode="HTML",
                reply_markup=keyboard
            )

            await query.answer(
                results=[result_photo],
                cache_time=5,
                is_personal=True
            )
            return

    # 2. Во всех остальных случаях (пустой запрос) — стандартная кнопка запуска Mini App
    try:
        await query.answer(
            results=[],
            cache_time=0,
            is_personal=True,
            button=InlineQueryResultsButton(
                text="🚲 Подбор вела, размера и каталог",
                start_parameter="catalog"
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
