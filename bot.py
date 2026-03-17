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

# Тут бот запам'ятовує:
# message_id повідомлення, яке він надіслав адміну -> user_id користувача
admin_reply_map = {}

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
async def handle_messages(message: Message):
    # 1) Повідомлення від користувача -> переслати адміну
    if message.chat.type == "private" and message.from_user.id != ADMIN_ID:
        username = f"@{message.from_user.username}" if message.from_user.username else "немає"
        text = message.text or message.caption or "[не текстове повідомлення]"

        sent_to_admin = await bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "📩 Нове повідомлення від користувача\n\n"
                f"Ім'я: {message.from_user.full_name}\n"
                f"Username: {username}\n"
                f"User ID: {message.from_user.id}\n\n"
                f"Текст:\n{text}\n\n"
                "↩️ Відповідай саме через Reply на це повідомлення."
            )
        )

        admin_reply_map[sent_to_admin.message_id] = message.from_user.id
        return

    # 2) Повідомлення від адміна -> відправити користувачу
    if message.chat.type == "private" and message.from_user.id == ADMIN_ID:
        if not message.reply_to_message:
            await message.answer("❗ Відповідай через Reply на повідомлення користувача.")
            return

        replied_message_id = message.reply_to_message.message_id
        target_user_id = admin_reply_map.get(replied_message_id)

        if not target_user_id:
            await message.answer("❗ Не знайшов, кому відправити. Відповідай саме на повідомлення, яке бот прислав тобі.")
            return

        reply_text = message.text or message.caption or "[порожнє повідомлення]"

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
