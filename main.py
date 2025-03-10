import asyncio
import os
import signal
import sys
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from contextlib import suppress

from config import BOT_TOKEN, SUPPORTED_IMAGE_FORMATS, SUPPORTED_VIDEO_FORMATS
from keyboards import get_start_keyboard, get_processing_keyboard
from utils.media_processor import MediaProcessor
from utils.logger import setup_logger

# Initialize the logger
logger = setup_logger()

# Global variables for storing temporary files
TEMP_FILES = set()

class UserState(StatesGroup):
    choosing_type = State()
    processing_sticker = State()
    processing_emoji = State()

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

def cleanup_temp_files():
    """Cleaning temporary files"""
    for file_path in TEMP_FILES:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Error removing temp file {file_path}: {e}")
    TEMP_FILES.clear()

async def shutdown(dispatcher: Dispatcher):
    """Correct termination of the bot"""
    logger.info("Bot shutdown...")
    
    # Clearing temporary files
    cleanup_temp_files()
    
    # Close connections and clear storage
    await dispatcher.storage.close()
    
    # Cancel all tasks
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    
    logger.info("Bot successfully stopped")

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Handle /start command"""
    await state.set_state(UserState.choosing_type)
    await message.answer(
        "Welcome! Choose what you want to create:",
        reply_markup=get_start_keyboard()
    )

@dp.message(UserState.choosing_type)
async def process_type_choice(message: types.Message, state: FSMContext):
    """Handle user's choice between sticker and emoji"""
    if message.text == "Create Sticker":
        await state.set_state(UserState.processing_sticker)
        await message.answer(
            "Send me an image or video to create a sticker.",
            reply_markup=get_processing_keyboard()
        )
    elif message.text == "Create Emoji":
        await state.set_state(UserState.processing_emoji)
        await message.answer(
            "Send me an image or video to create an emoji.",
            reply_markup=get_processing_keyboard()
        )

@dp.message(lambda message: message.text == "Back to Start")
async def back_to_start(message: types.Message, state: FSMContext):
    """Handle returning to start"""
    await cmd_start(message, state)

async def process_media(message: types.Message, is_sticker: bool):
    """Process media file and send result back to user"""
    temp_path = None
    result_path = None
    
    try:
        # Download file
        logger.info("=== Starting new file processing ===")
        if message.document:
            logger.info("Processing document")
            file_id = message.document.file_id
            file_name = message.document.file_name
            logger.info(f"Document name: {file_name}")
        elif message.photo:
            logger.info("Processing photo")
            file_id = message.photo[-1].file_id
            file_name = f"photo_{file_id}.jpg"
        elif message.video:
            logger.info("Processing video")
            file_id = message.video.file_id
            file_name = f"video_{file_id}.mp4"
        else:
            logger.warning("No media found in message")
            await message.answer("Please send an image or video file.")
            return

        logger.info(f"Getting file info for file_id: {file_id}")
        file = await bot.get_file(file_id)
        file_path = file.file_path
        logger.info(f"File path from Telegram: {file_path}")
        downloaded_file = await bot.download_file(file_path)

        # Save file temporarily
        temp_path = f"temp_{file_name}"
        logger.info(f"Saving to temp path: {temp_path}")
        
        with open(temp_path, "wb") as f:
            f.write(downloaded_file.read())
        
        logger.info(f"Temp file saved, size: {os.path.getsize(temp_path)} bytes")
        logger.info(f"Temp file exists: {os.path.exists(temp_path)}")

        # Process file
        logger.info("=== Starting MediaProcessor ===")
        processor = MediaProcessor(temp_path, is_sticker)
        logger.info("Created MediaProcessor instance")
        result_path, was_modified = processor.process()
        logger.info(f"Processing completed. Result path: {result_path}")
        logger.info(f"Result file exists: {os.path.exists(result_path)}")
        if os.path.exists(result_path):
            logger.info(f"Result file size: {os.path.getsize(result_path)} bytes")

        if not os.path.exists(result_path):
            logger.error("Error: Result file does not exist!")
            await message.answer("Error: Failed to process file")
            return

        # Send result
        logger.info("=== Sending file ===")
        with open(result_path, "rb") as f:
            file_data = f.read()
            logger.info(f"Read file data, size: {len(file_data)} bytes")
            await message.answer_document(
                types.BufferedInputFile(
                    file_data,
                    filename=os.path.basename(result_path)
                ),
                caption="Here's your processed file!" + 
                       (" (No modifications needed)" if not was_modified else "")
            )
            logger.info("File sent successfully")

        # Cleanup
        logger.info("=== Cleanup ===")
        if temp_path and os.path.exists(temp_path):
            logger.info(f"Removing temp file: {temp_path}")
            os.remove(temp_path)
            logger.info(f"Temp file removed: {not os.path.exists(temp_path)}")
        
        if result_path and result_path != temp_path and os.path.exists(result_path):
            logger.info(f"Removing result file: {result_path}")
            os.remove(result_path)
            logger.info(f"Result file removed: {not os.path.exists(result_path)}")

    except Exception as e:
        logger.error("=== Error ===")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error message: {str(e)}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        await message.answer(f"Error processing your file: {str(e)}")

@dp.message(UserState.processing_sticker)
async def process_sticker_file(message: types.Message):
    """Handle file for sticker creation"""
    if message.text == "Back to Start":
        return
    
    logger.info("Message content type: %s", message.content_type)
    logger.info("Message has photo: %s", bool(message.photo))
    logger.info("Message has document: %s", bool(message.document))
    logger.info("Message has video: %s", bool(message.video))
    
    if message.document:
        logger.info("Document mime_type: %s", message.document.mime_type)
        logger.info("Document file_name: %s", message.document.file_name)
    
    await process_media(message, is_sticker=True)

@dp.message(UserState.processing_emoji)
async def process_emoji_file(message: types.Message):
    """Handle file for emoji creation"""
    if message.text == "Back to Start":
        return
    await process_media(message, is_sticker=False)

async def main():
    """Start the bot"""
    # Configure SIGINT signal processing (Ctrl+C)
    def signal_handler(sig, frame):
        """Обработчик сигнала SIGINT"""
        logger.info("Получен сигнал на завершение...")
        asyncio.create_task(shutdown(dp))
        sys.exit(0)
    
    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        logger.info("The bot is running. To stop, press Ctrl+C")
        await dp.start_polling(bot)
    finally:
        await shutdown(dp)

if __name__ == "__main__":
    asyncio.run(main()) 
