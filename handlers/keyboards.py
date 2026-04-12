from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton




def get_cancel_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard= [
            [KeyboardButton(text="Отмена")],
        ]
    )
    return keyboard

def get_main_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            
            [KeyboardButton(text="PDF to JPG(webp)"), KeyboardButton(text="Узнать айди стикера")],
            [KeyboardButton(text="Изменить размер фото"), KeyboardButton(text="Получить стикер из фото")],
            [KeyboardButton(text="Скачать видео из тиктока без водяного знака")],
            
        ],
        resize_keyboard=True
    )
    return keyboard