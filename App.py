import requests
import json
from pydantic import BaseModel
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

API_TOKEN = "e4oEaZY1Kom5OXzybETkMlwjOCy3i8GSCGTHzWrhd4dc563b" 
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WHITE_LIST = set()

class IMEIRequest(BaseModel):
    imei: str
    token: str

def validate_imei(imei: str) -> bool:
    return len(imei) == 15 and imei.isdigit()

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_command(message: Message):
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Добавиться в белый список", callback_data="add_to_whitelist")
    keyboard.add(button)
    await message.reply("Привет! Нажмите кнопку ниже, чтобы получить доступ.", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data == "add_to_whitelist")
async def add_to_whitelist(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id in WHITE_LIST:
        await callback_query.answer("Вы уже в белом списке!")
    else:
        WHITE_LIST.add(user_id)
        await callback_query.answer("Вы добавлены в белый список!")
        await callback_query.message.reply("Теперь вы можете пользоваться ботом.")

@dp.message_handler()
async def handle_message(message: Message):
    user_id = message.from_user.id
    if user_id not in WHITE_LIST:
        await message.reply("У вас нет доступа к боту.")
        return
    
    imei = message.text.strip()
    if not validate_imei(imei):
        await message.reply("Неверный формат IMEI. Должно быть 15 цифр.")
        return
    
    url = "https://api.imeicheck.net/v1/checks"
    payload = json.dumps({
        "deviceId": imei,
        "serviceId": 12  
    })
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Accept-Language': 'en',
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    if response.status_code == 200 or 201:
        await message.reply(response.text)
    else:
        await message.reply("Ошибка при проверке IMEI.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
