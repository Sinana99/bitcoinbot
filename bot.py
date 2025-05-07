import os
import time
import tweepy
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException

load_dotenv()

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')  
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

MIN_TWEET_INTERVAL = 4 * 3600

def get_bitcoin_data():
    try:
        client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

        klines = client.get_klines(
            symbol='BTCUSDT',
            interval=Client.KLINE_INTERVAL_4HOUR,
            limit=96
        )

        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col].astype(float)

        return df

    except BinanceAPIException as e:
        print(f"Binance API Error: {e}")
        return None
    except Exception as e:
        print(f"Error fetching Bitcoin data: {e}")
        return None

def find_simple_support_resistance(df):
    try:
        if df is None or df.empty:
            return None, None, None

        current_price = float(df['close'].iloc[-1])

        simple_support = df['low'].min()

        simple_resistance = df['high'].max()

        print(f"Identified simple support level: ${simple_support:,.2f}")
        print(f"Identified simple resistance level: ${simple_resistance:,.2f}")

        return current_price, simple_support, simple_resistance

    except Exception as e:
        print(f"Error finding simple support/resistance: {e}")
        return None, None, None

def is_near_level(price, level, threshold=0.005):
    if level is None:
        return False

    if abs(price - level) / level < threshold:
        return True
    return False

def post_tweet(price, level, level_type):
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        emoji = "🟢" if level_type == "support" else "🔴"
        tweet_text = f"{emoji} Bitcoin Price Alert {emoji}\n\n" \
                     f"Current Price: ${price:,.2f}\n" \
                     f"Approaching {level_type.upper()} level at: ${level:,.2f}\n" \
                     f"Time: {current_time}\n\n" \
                     f"#Bitcoin #BTC #Crypto #Trading #{level_type.capitalize()}Resistance"

        response = client.create_tweet(text=tweet_text)
        print(f"Successfully posted tweet: {tweet_text}")

    except tweepy.TweepyException as e:
        print(f"Twitter API Error: {e}")
    except Exception as e:
        print(f"Error posting tweet: {e}")

def main():
    print("Starting Simplified Bitcoin Support/Resistance Monitor Bot...")
    print("Using Binance API for 4-hour price data")

    last_tweet_time = 0
    last_tweeted_level = None

    while True:
        try:
            df = get_bitcoin_data()
            if df is not None and not df.empty:
                current_price, simple_support, simple_resistance = find_simple_support_resistance(df)

                if current_price is not None:
                    print(f"Current Bitcoin price: ${current_price:,.2f}")

                    current_time = time.time()

                    if True: #is_near_level(current_price, simple_support):
                        if (current_time - last_tweet_time) >= MIN_TWEET_INTERVAL and last_tweeted_level != simple_support:
                            print(f"Price ${current_price:,.2f} is near simple support at ${simple_support:,.2f}. Posting tweet...")
                            post_tweet(current_price, simple_support, "support")
                            last_tweet_time = current_time
                            last_tweeted_level = simple_support

                    elif is_near_level(current_price, simple_resistance):
                        if (current_time - last_tweet_time) >= MIN_TWEET_INTERVAL and last_tweeted_level != simple_resistance:
                            print(f"Price ${current_price:,.2f} is near simple resistance at ${simple_resistance:,.2f}. Posting tweet...")
                            post_tweet(current_price, simple_resistance, "resistance")
                            last_tweet_time = current_time
                            last_tweeted_level = simple_resistance

                    else:
                        last_tweeted_level = None
                        print("Price is not near simple support or resistance.")

                else:
                     print("Could not determine current price or simple levels.")

            else:
                print("Failed to fetch Bitcoin data.")

            print("Waiting for 30 minutes before next check...")
            time.sleep(1800)

        except Exception as e:
            print(f"Error in main loop: {e}")
            print("Waiting for 5 minutes before retrying after error...")
            time.sleep(300)

if __name__ == "__main__":
    main()
