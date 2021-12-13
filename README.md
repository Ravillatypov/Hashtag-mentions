# Hashtag mentions
Telegram bot for mentioning by hashtags in groups

## Usage
```
docker pull ghcr.io/ravillatypov/hashtag_mentions:latest
docker run -d -e TELEGRAM_TOKEN=your-telegram-bot-token ghcr.io/ravillatypov/hashtag_mentions:latest
```

## Configuration
TELEGRAM_TOKEN - telegram bot token
DB_URL - database url. By default is sqlite:///db/db.sqlite3
