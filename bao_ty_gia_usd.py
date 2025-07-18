import time
import requests
import datetime

# ==== CẤU HÌNH ====
TELEGRAM_BOT_TOKEN = "7447323319:AAEJEQ22pR-duNY9cflIiu6ibDNujrdir28"
TELEGRAM_CHAT_ID = "-4826132440"
HIBT_API_URL = "https://api.hibt0.com/otc/calculator/exchange-rate?langCode=vi_VN"

def get_chat_id():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        print(f"📥 Phát hiện chat_id: {res.json()} ")
        for update in data.get("result", []):
            chat = update.get("message", {}).get("chat", {})
            chat_id = chat.get("id")
            chat_title = chat.get("title") or chat.get("username") or "(no title)"
            if chat_id:
                print(f"📥 Phát hiện chat_id: {chat_id} ({chat_title})")
    except Exception as e:
        print("❌ Không lấy được chat_id:", e)

def get_hibt_rate():
    try:
        res = requests.get(HIBT_API_URL, timeout=10)
        res.raise_for_status()
        data = res.json()
        for item in data["data"]:
            if item["exchangeName"] == "HIBT":
                return {
                    "buy": item["exchangeRateBuy"],
                    "sell": item["exchangeRateSell"]
                }
    except Exception as e:
        print("❌ Lỗi khi lấy tỷ giá:", e)
    return None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        res = requests.post(url, data=payload, timeout=10)
        res.raise_for_status()
        print("✅ Gửi Telegram thành công:", res.json())
    except Exception as e:
        print("❌ Lỗi gửi Telegram:", e)

# === Theo dõi mỗi phút 1 lần ===
last_rate = None

print("🕒 Đang theo dõi tỷ giá USDT/VND từ HIBT...")
while True:
    rate = get_hibt_rate()
    if rate:
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        msg = (
            "📊 *Tỷ giá USDT - VNĐ*\n\n" 
            f"🕒 *Thời gian:* `{now}`\n"
            f"💵 *Giá mua:* `{rate['buy']:,}` VND\n" 
            f"💴 *Giá bán:* `{rate['sell']:,}` VND"
        )
        if rate != last_rate:
            print(msg)
            send_telegram(f"🔔 Tỷ giá thay đổi:\n{msg}")
            last_rate = rate
        else:
            print(f"✓ Không thay đổi: {msg}")
    else:
        print("⚠️ Không lấy được dữ liệu.")
    
    time.sleep(60)