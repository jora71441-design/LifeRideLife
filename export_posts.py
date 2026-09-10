import json
import re
import urllib.request
from bs4 import BeautifulSoup


def parse_channel():
    all_posts = []
    before_id = None
    processed_ids = set()

    print("🚀 Начинаем считывание ВСЕЙ истории канала @LifeRideLife...")

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

        new_count = 0
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

            price_match = re.search(
                r"(\d[\d\s]*\s*₽|\d[\d\s]*\s*€|\d[\d\s]*\s*\$)", text
            )
            price = price_match.group(1) if price_match else "По запросу"

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
            new_count += 1

        if min_msg_id is None or (before_id and min_msg_id >= before_id):
            break

        before_id = min_msg_id

    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)

    print(
        f"🎉 ГОТОВО! Собрано {len(all_posts)} товаров и сохранено в products.json"
    )


if __name__ == "__main__":
    parse_channel()
