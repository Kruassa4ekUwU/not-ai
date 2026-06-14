import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from database import Database
from neural import MarkovModel
from search import web_search

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database()
model = MarkovModel()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Я учусь на ваших сообщениях. Тегните меня чтобы получить ответ.")

@dp.message(Command("stats"))
async def stats(message: types.Message):
    count = db.get_message_count()
    vocab = model.vocab_size()
    await message.answer(f"📊 Сообщений в базе: {count}\n🧠 Слов в модели: {vocab}")

@dp.message(F.text)
async def handle_message(message: types.Message):
    if not message.text:
        return

    text = message.text.strip()
    bot_info = await bot.get_me()
    mention = f"@{bot_info.username}"

    # Сохраняем сообщение и обучаемся
    if mention not in text:
        db.save_message(text, message.chat.id)
        model.train(text)
        return

    # Бот тегнули — отвечаем
    query = text.replace(mention, "").strip()

    response = None

    # Если вопрос — ищем в интернете
    if query and any(w in query.lower() for w in ["что", "кто", "когда", "где", "как", "почему", "зачем", "?"]):
        search_result = await web_search(query)
        if search_result:
            response = search_result

    # Если нет результата из интернета — генерируем из модели
    if not response:
        response = model.generate(query if query else None)

    if response:
        await message.reply(response)
    else:
        await message.reply("Ещё учусь... Напишите побольше сообщений!")

async def main():
    db.init()
    # Загружаем существующие сообщения в модель при старте
    messages = db.get_all_messages()
    if messages:
        logging.info(f"Загружаю {len(messages)} сообщений в модель...")
        for msg in messages:
            model.train(msg)
        logging.info("Модель готова!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
