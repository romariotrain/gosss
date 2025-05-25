import random
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

TOKEN = "8131725923:AAFJkvXP0mxUvUif8I-0Kx4h9cqaWnjztdw"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Загружаем вопросы
with open('questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Клавиатура с кнопкой "Новые вопросы"
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔄 Новые вопросы")]],
    resize_keyboard=True
)


def select_questions():
    # Разделение вопросов по категориям
    uk_questions = [q for q in questions if q['uk_code'].startswith('УК')]
    opk_questions = [q for q in questions if q['uk_code'].startswith('ОПК')]
    pk_questions = [q for q in questions if q['uk_code'].startswith('ПК')]

    # Выбираем 2 уникальных УК
    uk_codes = list({q['uk_code'] for q in uk_questions})
    selected_uk = random.sample(uk_codes, min(2, len(uk_codes)))

    # Выбираем 2 уникальных ОПК/ПК (не повторяя цифры)
    opk_pk_questions = opk_questions + pk_questions
    opk_pk_codes = list({q['uk_code'] for q in opk_pk_questions})

    forbidden_numbers = [int(code.split('-')[1]) for code in selected_uk]
    available_codes = [
        code for code in opk_pk_codes
        if int(code.split('-')[1]) not in forbidden_numbers
    ]

    selected_opk_pk = random.sample(available_codes, min(2, len(available_codes)))

    # Собираем вопросы
    result = []
    for code in selected_uk:
        pool = [q for q in uk_questions if q['uk_code'] == code]
        result.append(random.choice(pool))

    for code in selected_opk_pk:
        pool = [q for q in opk_pk_questions if q['uk_code'] == code]
        result.append(random.choice(pool))

    random.shuffle(result)
    return result


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Нажмите кнопку ниже, чтобы начать тестирование:",
        reply_markup=main_keyboard
    )


@dp.message(lambda m: m.text == "🔄 Новые вопросы")
async def new_questions(message: types.Message):
    selected = select_questions()

    for q in selected:
        index = questions.index(q)  # Получаем индекс в общем списке
        btn = InlineKeyboardButton(
            text="🔍 Показать ответ",
            callback_data=f"ans_{index}"
        )
        await message.answer(
            f"📌 {q['uk_code']}\n❓ {q['text']}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[btn]])
        )


@dp.callback_query(lambda c: c.data.startswith('ans_') or c.data.startswith('hide_'))
async def toggle_answer(callback: types.CallbackQuery):
    data = callback.data
    index = int(data.split('_')[1])

    if index >= len(questions):
        await callback.answer("Вопрос не найден.")
        return

    question = questions[index]

    if data.startswith("ans_"):
        text = f"📌 {question['uk_code']}\n❓ {question['text']}\n\n📝 <b>Ответ:</b>\n{question['answer']}"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🙈 Скрыть ответ", callback_data=f"hide_{index}")]]
        )
    else:
        text = f"📌 {question['uk_code']}\n❓ {question['text']}"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🔍 Показать ответ", callback_data=f"ans_{index}")]]
        )

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        await callback.answer("Не удалось обновить сообщение.")
        return

    await callback.answer()


@dp.message(lambda m: m.sticker is not None)
async def on_sticker(message: types.Message):
    await message.answer_sticker(message.sticker.file_id)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

