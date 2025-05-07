# Bitcoin Price Twitter Bot

This bot posts the current Bitcoin price to Twitter once daily.

## Setup

1. Create a Twitter Developer account and get your API credentials
2. Create a `.env` file with the following variables:
```
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the bot:
```bash
python bot.py
```

## Features
- Posts Bitcoin support and resistance level alerts
- Uses Binance API for price data
- Automatically schedules posts 