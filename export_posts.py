import json
import re
import urllib.request
from bs4 import BeautifulSoup


def extract_price(text):
    # 1. Удаляем хэштеги, чтобы теги вида #150_250k не сбивали поиск
    clean_text = re.sub(r"#[a-zA-Z0-9_а-яА-ЯёЁ]+", "", text)

    # 2. Ищем ценовую строку по ключевым меткам из постов (💰 или "Цена:")
    price_line_match = re.search(
        r"(?:💰|Цена:?)\s*([\d\s\.]+\s*(?:₽|€|\$|руб|рублей|k|к)?)",
        clean_text,
        re.IGNORECASE,
    )
    if price_line_match:
        found_price = price_line_match.group(1).strip()
        # Приводим к красивому виду, если там просто цифры с пробелом
        if re.search(r"\d", found_price):
            if not re.search(r"(₽|€|\$|руб|k|к)", found_price, re.IGNORECASE):
                found_price += " ₽"
            return found_price

    # 3. Ищем явные суммы с валютой в очищенном тексте (например: 248 000₽)
    price_match = re.search(
        r"(\d[\d\s\.]*)\s*(₽|€|\$|руб|рублей)", clean_text, re.IGNORECASE
    )
    if price_match:
        val_str = price_match.group(1).strip()
        unit = price_match.group(2)
        if unit.lower() in ["руб", "рублей"]:
            unit = "₽"
        return f"{val_str} {unit}"

    # 4. Поиск сумм с "к" / "k" (например: 248к), но НЕ из хэштегов
    k_match = re.search(r"(\d+[\d\s\.]*)\s*[кkKК]\b", clean_text)
    if k_match:
        val = k_match.group(1).replace(" ", "").replace(".", "")
        try:
            return f"{int(val):,} ₽".replace(",", " ")
        except:
            return f"{k_match.group(1)} 000 ₽"

    # 5. Поиск больших чисел от 10 000
    num_match = re.search(r"(\b\d{2,3}[\s\.]?\d{3}\b)", clean_text)
    if num_match:
        return f"{num_match.group(1)} ₽"

    return "По запросу"


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

            text = text_el.get_text("\n")
            tags = re.findall(r"#[a-zA-Z0-9_а-яА-ЯёЁ]+", text)

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

            lines = [l.strip() for l in text.split("\n") if l.strip()]
            title = (
                re.sub(r"#[^\s]+", "", lines[0]).strip() if lines else "Товар"
            )

            # Извлечение точной цены
            price = extract_price(text)

            all_posts.append(
                {
                    "id": msg_id,
                    "title": title or "Товар LifeRideLife",
                    "rawText": text,
                    "tags": [t.lower() for t in tags],
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
