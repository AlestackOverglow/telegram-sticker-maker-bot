from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # The token must be in the .env file.

# Telegram static sticker requirements
STATIC_STICKER_MAX_SIZE = 512  # KB
STATIC_STICKER_WIDTH = 512
STATIC_STICKER_HEIGHT = 512
STATIC_STICKER_FORMAT = 'PNG'  

# Telegram animated sticker requirements
ANIMATED_STICKER_MAX_SIZE = 256  # KB
ANIMATED_STICKER_WIDTH = 512
ANIMATED_STICKER_HEIGHT = 512
ANIMATED_STICKER_FORMAT = 'WEBM'  # Telegram requires WEBM for animated stickers
ANIMATED_STICKER_FPS = 30
ANIMATED_STICKER_MAX_DURATION = 3  # seconds

# Telegram static emoji requirements
STATIC_EMOJI_MAX_SIZE = 100  # KB
STATIC_EMOJI_WIDTH = 100
STATIC_EMOJI_HEIGHT = 100
STATIC_EMOJI_FORMAT = 'PNG'  # Telegram requires PNG for static emoji

# Telegram animated emoji requirements
ANIMATED_EMOJI_MAX_SIZE = 100  # KB
ANIMATED_EMOJI_WIDTH = 100
ANIMATED_EMOJI_HEIGHT = 100
ANIMATED_EMOJI_FORMAT = 'WEBM'  # Telegram requires WEBM for animated emojis
ANIMATED_EMOJI_FPS = 30
ANIMATED_EMOJI_MAX_DURATION = 3  # seconds

# Supported formats
STATIC_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
ANIMATED_IMAGE_FORMATS = ['.gif', '.mp4', '.webm', '.avi']


# Supported formats
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.webm'] 