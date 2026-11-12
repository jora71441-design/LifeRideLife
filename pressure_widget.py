import os
import time
import html
import urllib.request
import json
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineQueryResultPhoto,
    InlineQueryResultsButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from github_uploader import ADMIN_ID, resolve_repo_path, commit_file_to_github
from pressure_widget import send_pressure_widget

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL", "https://liferidelife.onrender.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

PRODUCTS_URL = "https://jora71441-design.github.io/LifeRideLife/products.json"
BASE_IMG_URL = "https://jora71441-design.github.io/LifeRideLife"

_catalog_cache = {"timestamp": 0, "items": {}}


def get_cached_products():
    now = time.time()
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


@dp.message(Command("ping", "start"))
async def cmd_ping(message: types.Message):
    if message.from_user and message.from_user.id == ADMIN_ID:
        await message.answer(
            "🟢 Бот на связи и готов принимать файлы для GitHub.\n"
            "• Отправь файл документом — залью в репозиторий.\n"
            "• Отправь /test_calc — протестировать микровиджет давления (Bot API 10.4)."
        )
    else:
        await message.answer(
            "👋 Привет! Нажми кнопку «Каталог» ниже, чтобы подобрать велосипед или комплектующие.\n"
            "• /calc — калькулятор давления в шинах"
        )


@dp.message(Command("test_calc", "calc"))
async def cmd_test_calc(message: types.Message):
    """Отправляет тестовый HTML-микровиджет калькулятора давления в шинах."""
    ok, err = await send_pressure_widget(message.chat.id)
    if not ok:
        await message.answer(
            f"⚠️ Не удалось отрисовать микровиджет <code>sendWidget</code>:\n"
            f"<code>{html.escape(err)}</code>",
            parse_mode="HTML"
        )


@dp.message(F.document)
async def handle_admin_document(message: types.Message):
    """Принимает файлы кода только от администратора и коммитит их в GitHub."""
    if not message.from_user or message.from_user.id != ADMIN_ID:
        return

    doc = message.document
    filename = doc.file_name or "uploaded_file"
    status_msg = await message.answer(
        f"⏳ Загружаю <code>{filename}</code> в GitHub...",
        parse_mode="HTML"
    )

    try:
        file_info = await bot.get_file(doc.file_id)
        file_io = await bot.download_file(file_info.file_path)
        file_bytes = file_io.read()

        repo_path = resolve_repo_path(filename, message.caption)
        success, report = commit_file_to_github(file_bytes, repo_path)
        await status_msg.edit_text(
            report,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        await status_msg.edit_text(
            f"❌ Ошибка обработки файла: <code>{html.escape(str(e))}</code>",
            parse_mode="HTML"
        )


@dp.inline_query()
async def inline_query_handler(query: types.InlineQuery):
    q = (query.query or "").strip().lower()

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
    await bot.set_webhook(
        WEBHOOK_URL,
        allowed_updates=["message", "inline_query", "callback_query"],
        drop_pending_updates=False
    )
    print(f"Webhook установлен на: {WEBHOOK_URL}")


def main():
    dp.startup.register(on_startup)
    app = web.Application()

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
