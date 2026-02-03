import requests
from bs4 import BeautifulSoup
import json
import time
from tqdm import tqdm

def parse_telegram_channel(channel_username, limit=100, delay=1):
    """
    Парсит публичный Telegram-канал и возвращает последние посты в виде списка словарей.
    
    Args:
        channel_username (str): Имя канала без @, например "example_channel"
        limit (int): Сколько последних постов собрать
        delay (float): Задержка между запросами к веб-версии (сек)
    
    Returns:
        list: Список постов в формате [{"id": ..., "text": ...}]
    """
    base_url = f"https://t.me/s/{channel_username}"
    posts = []
    last_id = None  # Для пагинации через ?before=

    #while len(posts) < limit:
    for i in tqdm(range(0,limit)):
        url = base_url
        if last_id:
            url += f"?before={last_id}"
        
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Ошибка запроса: {resp.status_code}")
            break
        
        soup = BeautifulSoup(resp.text, "lxml")
        messages = soup.find_all("div", class_="tgme_widget_message_wrap")
        
        if not messages:
            break  # Больше постов нет

        for msg in messages:
            msg_id = msg.find("a", class_="tgme_widget_message_date")
            text_div = msg.find("div", class_="tgme_widget_message_text")
            
            if not msg_id or not text_div:
                continue

            post_id = int(msg_id.get("href").split("/")[-1])
            text = text_div.get_text(separator="\n").strip()
            
            posts.append({
                "id": post_id,
                "text": text
            })

            last_id = post_id  # Для пагинации

            if len(posts) >= limit:
                break

        time.sleep(delay)  # Защита от блокировок

    return posts

if __name__ == "__main__":
    channel = "REOSH_Sharapov"  # <-- замените на нужный канал без @
    posts = parse_telegram_channel(channel, limit=1000)

    # Сохраняем в JSON
    with open(f"{channel}_posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"Собрано {len(posts)} постов. Сохранено в {channel}_posts.json")
