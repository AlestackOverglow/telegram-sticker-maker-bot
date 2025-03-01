# Telegram Sticker Maker Bot

A Telegram bot that automatically process images and videos to meet Telegram's requirements for creating stickers and emojis in @Stickers. The bot maintains aspect ratios while resizing media to the correct dimensions and handles format conversion automatically.

This bot is designed with a session-based workflow: after choosing between sticker or emoji creation mode, it will continue processing all incoming media files in that mode until the user explicitly returns to the mode selection menu. This allows for efficient batch processing of multiple files without having to repeatedly select the desired output type.

If you find this project helpful, please consider giving it a star ⭐ It helps others discover the project and motivates further development.

## Branches
The bot has two versions available in different branches:
- `main` - Uses polling method to receive updates (recommended for development and testing)
- `webhook-version` - Uses webhook method to receive updates (recommended for production)

### Polling vs Webhook
- **Polling (main branch)**: 
  - Simpler to set up and debug
  - Works without public IP/domain
  - Suitable for development and testing
  - Higher resource usage due to constant requests

- **Webhook (webhook-version branch)**:
  - More efficient resource usage
  - Faster message processing
  - Requires HTTPS and public IP/domain
  - Better for production deployment
  - Supports dynamic webhook URL configuration

Choose the branch that best suits your needs before proceeding with installation.

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Logging](#logging)
- [Error Handling](#error-handling)
- [Shutdown](#shutdown)
- [Autostart on Linux](#autostart-on-linux)
- [Contributing](#contributing)
- [License](#license)

## Requirements
- Python 3.8+
- OpenCV (for video processing)
- Required Python packages (see requirements.txt)

## Installation
1. Clone the repository:
```bash
git clone https://github.com/AlestackOverglow/telegram-sticker-maker-bot.git
cd telegram-sticker-maker-bot
```

2. Create and activate virtual environment (recommended):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your bot token:
```
BOT_TOKEN=your_bot_token_here
```

## Usage
1. Start the bot:
```bash
python main.py
```

2. In Telegram:
   - Send `/start` to begin
   - Choose between creating a sticker or emoji
   - Send any supported media file
   - The bot will continue processing files in the chosen mode
   - Use "Back to Start" button to switch between sticker and emoji modes
   - The bot will automatically process and return each file in the correct format

## Features
- Creates both stickers and emoji from images and videos
- Supports various input formats:
  - Images: JPG, JPEG, PNG, WEBP
  - Videos: MP4, WEBM
  - Animated: GIF
- Automatically resizes media while maintaining aspect ratio
- Converts to required formats:
  - Static stickers: PNG (512x512px max, 512KB max)
  - Animated stickers: WEBM with VP9 codec (512x512px max, 256KB max)
  - Static emoji: PNG (100x100px max, 100KB max)
  - Animated emoji: WEBM with VP9 codec (100x100px max, 100KB max)
- Handles animated content:
  - Limits duration to 3 seconds
  - Sets frame rate to 30 FPS
  - Automatically adjusts bitrate to meet size requirements
- Simple button-based interface
- Automatic cleanup of temporary files
- Session-based workflow for efficient batch processing

## Logging
The bot logs all operations to `logs/bot.log` with automatic log rotation:
- Maximum log file size: 10MB
- Keeps last 5 log files
- Logs include timestamps and detailed processing information

## Error Handling
- Validates input file formats
- Checks file sizes and dimensions
- Provides detailed error messages
- Logs all errors with full tracebacks for debugging

## Shutdown
The bot can be safely stopped by pressing Ctrl+C. It will:
- Complete any ongoing file processing
- Clean up temporary files
- Close all connections properly

## Autostart on Linux
To run the bot as a service on Linux using systemd:

1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/stickmaker.service
```

2. Add the following configuration (adjust paths according to your setup):
```ini
[Unit]
Description=Telegram Sticker Maker Bot
After=network.target

[Service]
Type=simple
User=your_username
Group=your_group
WorkingDirectory=/path/to/telegram-sticker-maker-bot
Environment=PATH=/path/to/telegram-sticker-maker-bot/venv/bin
ExecStart=/path/to/telegram-sticker-maker-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl enable stickmaker
sudo systemctl start stickmaker
```

4. Check service status:
```bash
sudo systemctl status stickmaker
```

5. View logs:
```bash
# Service logs
sudo journalctl -u stickmaker -f

# Bot logs
tail -f /path/to/telegram-sticker-maker-bot/logs/bot.log
```

## Contributing
Feel free to submit issues and pull requests.

## License
[MIT License](LICENSE) 
