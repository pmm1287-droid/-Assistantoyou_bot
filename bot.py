import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from aiogram import Bot, Dispatcher
from aiogram.types import ChatJoinRequest, Message

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ВСТАВ СВІЙ TELEGRAM USER ID
ADMIN_ID = @b2bhelp001

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
    await bot.approve_chat_join_request(
        chat_id=join_request.chat.id,
        user_id=join_request.from_user.id
    )

    try:
        await bot.send_message(
            chat_id=join_request.user_chat_id,
            text=WELCOME_TEXT
        )
    except Exception:
        pass

@dp.message()
async def handle_all_messages(message: Message):
    # 1) Якщо це повідомлення від користувача боту в приват
    if message.chat.type == "private" and message.from_user.id != ADMIN_ID:
        username = f"@{message.from_user.username}" if message.from_user.username else "немає"
        text = message.text or "[не текстове повідомлення]"

        # Шлемо тобі повідомлення і вказуємо ID користувача
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
        return

    # 2) Якщо це твоє повідомлення боту, і ти відповідаєш на переслану картку
    if message.chat.type == "private" and message.from_user.id == ADMIN_ID:
        if not message.reply_to_message or not message.reply_to_message.text:
            return

        original_text = message.reply_to_message.text

        if "User ID:" not in original_text:
            return

        try:
            user_id_line = [line for line in original_text.splitlines() if line.startswith("User ID:")][0]
            target_user_id = int(user_id_line.replace("User ID:", "").strip())
        except Exception:
            await message.answer("Не зміг визначити user ID.")
            return

        reply_text = message.text or "[порожнє повідомлення]"

        try:
            await bot.send_message(
                chat_id=target_user_id,
                text=reply_text
            )
            await message.answer("✅ Відправлено користувачу")
        except Exception as e:
            await message.answer(f"❌ Не вдалося відправити: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    asyncio.run(main())
