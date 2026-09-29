# Discord Welcome Bot (Nexus Roleplay Edition)

A Discord.py v2.0+ bot that automatically sends a customized welcome message with rich embeds and action buttons when new members join your server.

## Features

✨ **Rich Embed Messages** - Beautiful, styled welcome messages matching the Nexus Roleplay aesthetic
📋 **Action Buttons** - Quick-access buttons for rules and visa applications
👥 **Member Count** - Displays current member count in the footer
⚡ **Easy Configuration** - Configurable constants at the top of the code
🔒 **Environment Variables** - Secure token and channel ID storage

## Installation

### 1. Install Python

Ensure you have Python 3.8+ installed. Download from [python.org](https://www.python.org/downloads/)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- **discord.py>=2.0.0** - Discord API library for Python
- **python-dotenv>=0.19.0** - Environment variable management

### 3. Configure Environment Variables

Create a `.env` file in the root directory (template provided) and fill in your values:

```
BOT_TOKEN=your_bot_token_here
WELCOME_CHANNEL_ID=your_welcome_channel_id_here
```

### 4. Enable Server Members Intent

To allow the bot to detect when members join, you must enable the **Server Members Intent** in Discord Developer Portal:

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your bot application
3. Navigate to **Bot** in the left sidebar
4. Under **PRIVILEGED GATEWAY INTENTS**, toggle **Server Members Intent** to ON
5. Save changes

⚠️ **Important**: If your bot is in 100+ servers, you may need to apply for verification. For development/testing, this usually isn't required.

## Configuration

Open `bot.py` and customize the constants at the top:

```python
SERVER_NAME = "Nexus Roleplay"          # Your server name
BANNER_IMAGE_URL = ""                   # Your banner image URL
RULES_URL = ""                          # Your Discord rules link
CITY_RULES_URL = ""                     # Your city rules link
APPLY_URL = ""                          # Your visa application link
```

## Inviting the Bot

To invite the bot to your server with the correct permissions:

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your bot application
3. Navigate to **OAuth2** → **URL Generator**
4. Under **SCOPES**, select:
   - ✅ `bot`
5. Under **PERMISSIONS**, select:
   - ✅ `Send Messages`
   - ✅ `Embed Links`
   - ✅ `Read Message History`
6. Copy the generated URL and open it in your browser to invite the bot

**Minimum Required Permissions:**
- Send Messages
- Embed Links

## Running the Bot

Start the bot with:

```bash
python bot.py
```

You should see a message like:
```
✅ Bot is online as YourBot#1234
```

## How It Works

1. Bot listens for the `on_member_join` event (new member joins)
2. Creates a rich embed message with:
   - Server name as author
   - Welcoming title
   - Member's avatar as thumbnail
   - Current member count and time in footer
   - Color: #CC0000 (dark red)
3. Adds three interactive buttons:
   - **Discord Rules** - Links to your rules page
   - **City Rules** - Links to your city rules page
   - **Apply Visa** - Links to your application form
4. Sends the message to your configured welcome channel

## Embed Preview

```
┌─────────────────────────────────────────┐
│ 👋 Welcome to Nexus Roleplay            │
│                                         │
│ ✨ Your next great story starts here.   │
│   Welcome to your new home,             │
│   Nexus Roleplay.                       │
│                                         │
│ We are excited to see the stories you   │
│ will create in our city. To get         │
│ started on your journey, please         │
│ review our community rules and submit   │
│ your application using the buttons      │
│ below.                                  │
│                                         │
│ [Discord Rules] [City Rules] [Apply]    │
│                                         │
│ Members: 250 • Today at 14:32            │
└─────────────────────────────────────────┘
```

## Troubleshooting

### Bot doesn't respond
- ✅ Check that `BOT_TOKEN` in `.env` is correct
- ✅ Verify the bot is online in Discord Developer Portal
- ✅ Ensure bot has permissions in the welcome channel

### No welcome message appears
- ✅ Verify `WELCOME_CHANNEL_ID` is correct
- ✅ Check bot has **Send Messages** permission in that channel
- ✅ Make sure **Server Members Intent** is enabled in Developer Portal
- ✅ Check console for error messages

### "WELCOME_CHANNEL_ID not set in .env file"
- ✅ Make sure your `.env` file exists in the root directory
- ✅ Make sure it contains `WELCOME_CHANNEL_ID=your_channel_id_here`
- ✅ Restart the bot after editing `.env`

### Module not found errors
- ✅ Make sure you installed dependencies: `pip install -r requirements.txt`
- ✅ Verify you're using Python 3.8 or higher: `python --version`

## Project Structure

```
discord-welcome-bot/
├── bot.py             # Main bot file
├── requirements.txt   # Python dependencies
├── .env              # Environment variables (NOT in git)
└── README.md         # This file
```

## Support

For issues with:
- **discord.py**: [discord.py Documentation](https://discordpy.readthedocs.io/)
- **Discord Bot Development**: [Discord Developer Portal](https://discord.com/developers/applications)
- **Python**: [Python Documentation](https://docs.python.org/)
