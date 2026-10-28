import io
import json
import os
import re
import urllib.request
from bs4 import BeautifulSoup
from PIL import Image


def clean_text(text):
    if not text:
        return ""
    # Удаляем скрытые невидимые символы
    text = text.replace('\u200b', '').replace('\ufeff', '')
    return text.strip()


def extract_price(text):
    clean_t = re.sub(r"#[a-zA-Z0-9_а-яА-ЯёЁ]+", "", text)

    price_line_match = re.search(
        r"(?:💰|Цена:?)\s*([\d\s\.]+\s*(?:₽|€|\$|руб|рублей|k|к)?)",
        clean_t,
        re.IGNORECASE,
    )
    if price_line_match:
        found_price = price_line_match.group(1).strip()
        if re.search(r"\d", found_price):
            found_price = re.sub(r"(\d)\.(\d{3})", r"\1 \2", found_price)
            if not re.search(r"(₽|€|\$|руб|k|к)", found_price, re.IGNORECASE):
                found_price += " ₽"
            return found_price

    price_match = re.search(
        r"(\d[\d\s\.]*)\s*(₽|€|\$|руб|рублей)", clean_t, re.IGNORECASE
    )
    if price_match:
        val_str = price_match.group(1).strip().replace(".", " ")
        unit = price_match.group(2)
        if unit.lower() in ["руб", "рублей"]:
            unit = "₽"
        return f"{val_str} {unit}"

    k_match = re.search(r"(\d+[\d\s\.]*)\s*[кkKК]\b", clean_t)
    if k_match:
        val = k_match.group(1).replace(" ", "").replace(".", "")
        try:
            return f"{int(val):,} ₽".replace(",", " ")
        except Exception:
            return f"{k_match.group(1)} 000 ₽"

    num_match = re.search(r"(\b\d{2,3}[\s\.]?\d{3}\b)", clean_t)
    if num_match:
        val = num_match.group(1).replace(".", " ")
        return f"{val} ₽"

    return "По запросу"


def determine_category(tags_lower, raw_text_lower):
    """Автоматическое определение категории поста"""
    if any(
            t in tags_lower for t in [
                "#отзыв",
                "#отзывы",
                "#покупка"]) or re.search(
        r"\bотзыв(?:ы|а|е|ом|ов)?\b",
            raw_text_lower):
        return "reviews"
    if any(
            t in tags_lower for t in [
                "#гайд",
                "#гайды",
                "#полезно",
                "#ростовка",
                "#обслуживание"]) or re.search(
        r"\bгайд(?:ы|а|е|ом|ов)?\b",
            raw_text_lower):
        return "guides"
    if any(
        t in tags_lower for t in [
            "#фреймсет",
            "#kit",
            "#upgrade",
            "#комплект"]):
        return "upgrade_kits"
    if any(
        t in tags_lower for t in [
            "#запчасти",
            "#компоненты",
            "#групсет",
            "#колеса",
            "#руль",
            "#седло"]):
        return "components"
    return "bikes"


def extract_title(text):
    """Поиск реального названия товара без эмодзи и статусов 'ПРОДАН'"""
    lines = [clean_text(l) for l in text.split("\n") if clean_text(l)]
    for line in lines:
        clean_line = re.sub(r"#[^\s]+", "", line).strip()
        clean_line_no_emoji = re.sub(r"[^\w\s\d-]", "", clean_line).strip()

        # Пропускаем пустые строки, чисто эмодзи и статусы "ПРОДАН"
        if clean_line_no_emoji and not re.match(
                r"^(продан|продано)$", clean_line_no_emoji.lower()):
            return clean_line
    return "Товар LifeRideLife"


def parse_channel():
    all_posts = []
    before_id = None
    processed_ids = set()

    # Создаем папку images 1 раз в самом начале
    os.makedirs("images", exist_ok=True)

    print("🚀 Начинаем считывание истории канала @LifeRideLife...")

    while True:
        url = "https://t.me/s/LifeRideLife"
        if before_id:
            url += f"?before={before_id}"

        req = urllib.request.Request(
            url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

        try:
            html = urllib.request.urlopen(req).read().decode("utf-8")
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            break

        soup = BeautifulSoup(html, "html.parser")
        messages = soup.find_all("div", class_="tgme_widget_message")

        if not messages:
            print("🏁 История закончилась!")
            break

        min_msg_id = None

        for msg in messages:
            post_link_el = msg.find("a", class_="tgme_widget_message_date")
            if not post_link_el or "href" not in post_link_el.attrs:
                continue

            post_url = post_link_el["href"]
            msg_id = int(post_url.split("/")[-1])

            if min_msg_id is None or msg_id < min_msg_id:
                min_msg_id = msg_id

            if msg_id in processed_ids:
                continue

            processed_ids.add(msg_id)

            text_el = msg.find("div", class_="tgme_widget_message_text")
            if not text_el:
                continue

            raw_text = clean_text(text_el.get_text("\n"))
            tags = re.findall(r"#[a-zA-Z0-9_а-яА-ЯёЁ]+", raw_text)

            if not tags:
                continue

            # Исключаем проданные позиции
            if any(t.lower() in ["#продано", "#продан"]
                   for t in tags) or "продан" in raw_text.lower()[:40]:
                continue

            photo_wrap = msg.find(
                "a", class_="tgme_widget_message_photo_wrap"
            ) or msg.find("div", class_="tgme_widget_message_photo_wrap")
            img_url = "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600"
            if photo_wrap and "style" in photo_wrap.attrs:
                match = re.search(
                    r"background-image:url\('([^']+)'\)", photo_wrap["style"]
                )
                if match:
                    remote_img_url = match[1]
                    filename = f"bike_{msg_id}.webp"
                    local_path = os.path.join("images", filename)

                    # Скачиваем и жмём в WebP только если файла ещё нет
                    if not os.path.exists(local_path):
                        try:
                            img_req = urllib.request.Request(
                                remote_img_url, headers={
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                            with urllib.request.urlopen(img_req, timeout=15) as resp:
                                img_bytes = resp.read()

                            with Image.open(io.BytesIO(img_bytes)) as pil_img:
                                if pil_img.mode in ("RGBA", "P"):
                                    pil_img = pil_img.convert("RGB")
                                # Ограничиваем максимальную сторону до 1200px
                                pil_img.thumbnail(
                                    (1200, 1200), Image.Resampling.LANCZOS)
                                pil_img.save(
                                    local_path, "WEBP", quality=80, method=6)

                            img_url = f"./images/{filename}"
                        except Exception as e:
                            print(
                                f"⚠️ Ошибка сжатия фото для поста {msg_id}: {e}")
                            img_url = remote_img_url
                    else:
                        img_url = f"./images/{filename}"

            title = extract_title(raw_text)
            price = extract_price(raw_text)

            # Нормализация хэштегов (заменяем 'к' на 'k' в бюджетах)
            normalized_tags = []
            for t in tags:
                t_lower = t.lower()
                t_lower = re.sub(r"#(\d+_\d+)к$", r"#\1k", t_lower)
                normalized_tags.append(t_lower)

            raw_text_lower = raw_text.lower()
            category = determine_category(normalized_tags, raw_text_lower)

            all_posts.append(
                {
                    "id": msg_id,
                    "title": title,
                    "category": category,
                    "rawText": raw_text,
                    "tags": normalized_tags,
                    "originalTagsText": " ".join(tags),
                    "imgUrl": img_url,
                    "price": price,
                    "postUrl": post_url,
                }
            )

        if min_msg_id is None or (before_id and min_msg_id >= before_id):
            break

        before_id = min_msg_id

    # Сохраняем общий каталог products.json
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)

    # Создаем папку share для генерации страниц предпросмотра (OG Preview)
    os.makedirs("share", exist_ok=True)
    base_repo_url = "https://jora71441-design.github.io/LifeRideLife"

    for post in all_posts:
        bike_id = post["id"]
        title = post.get(
            "title",
            "Велосипед LifeRideLife").replace(
            '"',
            '&quot;')
        price = post.get("price", "По запросу")
        img_rel = post.get("imgUrl", "")

        # Превращаем путь картинки в абсолютный для робота Telegram
        if img_rel.startswith("./"):
            og_img = f"{base_repo_url}/{img_rel[2:]}"
        elif img_rel.startswith("http"):
            og_img = img_rel
        else:
            og_img = f"{base_repo_url}/{img_rel}"

        target_app_url = f"https://t.me/liferidelife_bot?startapp=bike_{bike_id}"
        tg_native_url = f"tg://resolve?domain=liferidelife_bot&startapp=bike_{bike_id}"

        html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — {price}</title>

  <!-- Open Graph / Telegram Preview Meta -->
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="LifeRideLife">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{price} • В наличии / под заказ в LifeRideLife">
  <meta property="og:image" content="{og_img}">
  <meta property="og:image:secure_url" content="{og_img}">
  <meta property="og:image:type" content="image/webp">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="800">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{price} • В наличии / под заказ в LifeRideLife">
  <meta name="twitter:image" content="{og_img}">

  <!-- Мгновенный переход через протокол tg:// -->
  <script>
    window.location.href = "{tg_native_url}";
    setTimeout(function() {{
      window.location.href = "{target_app_url}";
    }}, 300);
  </script>
</head>
<body style="background:#18222d; color:#fff; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; text-align:center; padding:40px 20px;">
  <h2 style="font-size:20px; margin-bottom:8px;">{title}</h2>
  <p style="color:#24a1de; font-size:18px; font-weight:bold; margin-bottom:20px;">{price}</p>
  <a href="{tg_native_url}" style="display:inline-block; background:#24a1de; color:#fff; padding:12px 24px; border-radius:10px; text-decoration:none; font-weight:bold; font-size:15px;">
    🚴‍♂️ Открыть в приложении LifeRideLife
  </a>
</body>
</html>"""

        with open(os.path.join("share", f"bike_{bike_id}.html"), "w", encoding="utf-8") as sf:
            sf.write(html_content)

    print(f"🎉 ГОТОВО! Собрано {len(all_posts)} товаров и сжаты фото в WebP.")


if __name__ == "__main__":
    parse_channel()
