import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from aiogram import Bot, Dispatcher
from aiogram.types import ChatJoinRequest, Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8415140381

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

WELCOME_TEXT = """Якщо ви хочете почати співпрацю, будь ласка, уважно ознайомтесь із наступними умовами:

⬇️ Для того щоб приєднатися до команди, потрібно виконати всі кроки, зазначені нижче.

❗️УВАЖНІСТЬ ТА ВИКОНАННЯ ВСІХ ВИМОГ — запорука успішної співпраці!

1️⃣ Реєстрацію необхідно пройти виключно за цим посиланням.

😎 https://gguapromo.com/l/694bf8aa934079ff9d09ee13?sub_id={sub_id_1}&click_id={click_id}
😎

(Якщо у вас вже є зареєстрований акаунт — обов’язково повідомте нам про це.)

Потрібно повністю завершити процес реєстрації: створити логін і пароль, а також пройти верифікацію.
(Через застосунок ДІЯ це займе лише близько 1 хвилини.)

2️⃣ Після того як реєстрація буде завершена, надішліть, будь ласка, скріншот вашого акаунта в особисті повідомлення.

Після перевірки менеджер вручну підтвердить вашу заявку в канал.

Бажаємо всім успіхів та сподіваємося на ефективну співпрацю! 🫡
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

        )
    except Exception as e:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"❌ Не вдалося написати користувачу {join_request.from_user.id}: {e}"
        )

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "🆕 Нова заявка в канал\n\n"
            f"Ім'я: {join_request.from_user.full_name}\n"
            f"Username: @{join_request.from_user.username if join_request.from_user.username else 'немає'}\n"
            f"User ID: {join_request.from_user.id}"
        )
    )

@dp.message()
async def handle_messages(message: Message):
    if message.chat.type != "private":
        return

    # Твої власні повідомлення боту можна ігнорувати
    if message.from_user.id == ADMIN_ID:
        return

    username = f"@{message.from_user.username}" if message.from_user.username else "немає"
    text = message.text or message.caption or "[не текстове повідомлення]"

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📩 Нове повідомлення від користувача\n\n"
            f"Ім'я: {message.from_user.full_name}\n"
            f"Username: {username}\n"
            f"User ID: {message.from_user.id}\n\n"
            f"Текст:\n{text}"
        )
    )

    await message.answer(
        "Ваше повідомлення отримано. Після перевірки менеджер вручну підтвердить заявку в канал."
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    asyncio.run(main())
