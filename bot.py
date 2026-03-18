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

# Зберігаємо заявки: user_id -> chat_id каналу
pending_requests = {}

WELCOME_TEXT = """Якщо ви хочете почати співпрацю, будь ласка, уважно ознайомтесь із наступними умовами:

⬇️ Для того щоб приєднатися до команди, потрібно виконати всі кроки, зазначені нижче.

❗️УВАЖНІСТЬ ТА ВИКОНАННЯ ВСІХ ВИМОГ — запорука успішної співпраці!

1️⃣ Реєстрацію необхідно пройти виключно за цим посиланням.

😎 https://gguapromo.com/l/694bf8aa934079ff9d09ee13?sub_id={sub_id_1}&click_id={click_id}
😎

(Якщо у вас вже є зареєстрований акаунт — обов’язково повідомте нам про це.)

Потрібно повністю завершити процес реєстрації: створити логін і пароль, а також пройти верифікацію.
(Через застосунок ДІЯ це займе лише близько 1 хвилини.)

2️⃣ Після того як реєстрація буде завершена, напишіть сюди слово: ГОТОВО

3️⃣ Після цього бот автоматично підтвердить вашу заявку в канал.

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

@dp.chat_join_request()
async def handle_join_request(join_request: ChatJoinRequest):
    user_id = join_request.from_user.id
    chat_id = join_request.chat.id

    # Зберігаємо заявку, але НЕ приймаємо її одразу
    pending_requests[user_id] = chat_id

    try:
        await bot.send_message(
            chat_id=join_request.user_chat_id,
            text=WELCOME_TEXT
        )
    except Exception as e:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"❌ Не вдалося написати користувачу {user_id}: {e}"
        )

@dp.message()
async def handle_messages(message: Message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    text = (message.text or message.caption or "").strip()

    # Твої власні повідомлення не чіпаємо
    if user_id == ADMIN_ID:
        return

    # Якщо користувач написав "готово" і в нього є заявка — підтверджуємо
    if text.lower() == "готово":
        chat_id = pending_requests.get(user_id)

        if not chat_id:
            await message.answer("Не знайшов активну заявку в канал. Подайте заявку ще раз.")
            return

        try:
            await bot.approve_chat_join_request(
                chat_id=chat_id,
                user_id=user_id
            )

            await message.answer("✅ Готово! Вашу заявку підтверджено. Тепер ви маєте доступ до каналу.")

            await bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "✅ Підтверджено заявку\n\n"
                    f"Ім'я: {message.from_user.full_name}\n"
                    f"Username: @{message.from_user.username if message.from_user.username else 'немає'}\n"
                    f"User ID: {user_id}"
                )
            )

            pending_requests.pop(user_id, None)

        except Exception as e:
            await message.answer("❌ Не вдалося підтвердити заявку. Напишіть менеджеру.")
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"❌ Помилка при підтвердженні заявки user_id={user_id}: {e}"
            )
        return

    # Будь-яке інше повідомлення пересилаємо тобі
    username = f"@{message.from_user.username}" if message.from_user.username else "немає"
    forwarded_text = text if text else "[не текстове повідомлення]"

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📩 Нове повідомлення від користувача\n\n"
            f"Ім'я: {message.from_user.full_name}\n"
            f"Username: {username}\n"
            f"User ID: {user_id}\n\n"
            f"Текст:\n{forwarded_text}"
        )
    )

    await message.answer(
        "Ваше повідомлення отримано. "
        "Коли завершите реєстрацію та верифікацію, напишіть словом: ГОТОВО"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    asyncio.run(main())
