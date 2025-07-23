from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder

admin_kb = ReplyKeyboardMarkup(
    keyboard = [[KeyboardButton(text="Добавление/изменение баннера"),
                KeyboardButton(text="Проверить на обновление")
                 ],
                [KeyboardButton(text="Создать новый нфт"),
                 KeyboardButton(text="Просмотреть админов")]],
    resize_keyboard=True)

