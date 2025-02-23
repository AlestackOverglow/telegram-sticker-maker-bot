from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_start_keyboard() -> ReplyKeyboardMarkup:
    """Create keyboard for initial choice between sticker and emoji"""
    keyboard = [
        [KeyboardButton(text="Create Sticker"), KeyboardButton(text="Create Emoji")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_processing_keyboard() -> ReplyKeyboardMarkup:
    """Create keyboard for when user is in processing mode"""
    keyboard = [[KeyboardButton(text="Back to Start")]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True) 