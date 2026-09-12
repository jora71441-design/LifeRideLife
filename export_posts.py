import json
import re
import urllib.request
from bs4 import BeautifulSoup


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
    if any(t in tags_lower for t in ["#отзыв", "#отзывы", "#покупка"]) or "отзыв" in raw_text_lower:
        return "reviews"
    if any(t in tags_lower for t in ["#гайд", "#гайды", "#полезно", "#ростовка", "#обслуживание"]) or "гайд" in raw_text_lower:
        return "guides"
    if any(t in tags_lower for t in ["#фреймсет", "#kit", "#upgrade", "#комплект"]):
        return "upgrade_kits"
    if any(t in tags_lower for t in ["#запчасти", "#компоненты", "#групсет", "#колеса", "#руль", "#седло"]):
        return "components"
    return "bikes"


def extract_title(text):
    """Поиск реального названия товара без эмодзи и статусов 'ПРОДАН'"""
    lines = [clean_text(l) for l in text.split("\n") if clean_text(l)]
    for line in lines:
        clean_line = re.sub(r"#[^\s]+", "", line).strip()
        clean_line_no_emoji = re.sub(r"[^\w\s\d-]", "", clean_line).strip()
        
        # Пропускаем пустые строки, чисто эмодзи и статусы "ПРОДАН"
        if clean_line_no_emoji and not re.match(r"^(продан|продано)$", clean_line_no_emoji.lower()):
            return clean_line
    return "Товар LifeRideLife"


def parse_channel():
    all_posts = []
    before_id = None
    processed_ids = set()

    print("🚀 Начинаем считывание истории канала @LifeRideLife...")

    while True:
        url = "https://t.me/s/LifeRideLife"
        if before_id:
            url += f"?before={before_id}"

        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )

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

            photo_wrap = msg.find(
                "a", class_="tgme_widget_message_photo_wrap"
            ) or msg.find("div", class_="tgme_widget_message_photo_wrap")
            img_url = "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600"
            if photo_wrap and "style" in photo_wrap.attrs:
                match = re.search(
                    r"background-image:url\('([^']+)'\)", photo_wrap["style"]
                )
                if match:
                    img_url = match[1]

            title = extract_title(raw_text)
            price = extract_price(raw_text)
            
            # Нормализация хэштегов (заменяем 'к' на 'k' в бюджетах для единообразия)
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

    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)

    print(f"🎉 ГОТОВО! Собрано {len(all_posts)} товаров.")


if __name__ == "__main__":
    parse_channel()
