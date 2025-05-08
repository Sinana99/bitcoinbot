import os
import time
import tweepy
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

        processed_data = []
        for kline in klines:
            timestamp = datetime.fromtimestamp(kline[0] / 1000)
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            processed_data.append({
                'timestamp': timestamp,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price
            })

        return processed_data

    except BinanceAPIException as e:
        print(f"Binance API Error: {e}")
        return None
    except Exception as e:
        print(f"Error fetching Bitcoin data: {e}")
        return None

def find_simple_support_resistance(data):
    try:
        if data is None or not data:
            print("No data provided to find support/resistance.")
            return None, None, None

        current_price = data[-1]['close']

        simple_support = min(item['low'] for item in data)
        simple_resistance = max(item['high'] for item in data)

        print(f"Identified simple support level: ${simple_support:,.2f}")
        print(f"Identified simple resistance level: ${simple_resistance:,.2f}")

        return current_price, simple_support, simple_resistance

    except Exception as e:
        print(f"Error finding simple support/resistance: {e}")
        return None, None, None

def is_near_level(price, level, threshold=100.0):
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
                     f"#Bitcoin #BTC #Crypto #Trading #{level_type.capitalize()}"

        response = client.create_tweet(text=tweet_text)
        print(f"Successfully posted tweet: {tweet_text}")

    except tweepy.TweepyException as e:
        print(f"Twitter API Error: {e}")
    except Exception as e:
        print(f"Error posting tweet: {e}")

def post_initial_tweet():
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )

        # Changed the tweet text to a simple generic message
        tweet_text = "Hello everyone! Bot is starting up. 👋"

        response = client.create_tweet(text=tweet_text)
        print(f"Successfully posted initial tweet: {tweet_text}")

    except tweepy.TweepyException as e:
        print(f"Twitter API Error posting initial tweet: {e}")
    except Exception as e:
        print(f"Error posting initial tweet: {e}")


def main():
    print("Starting Simplified Bitcoin Support/Resistance Monitor Bot...")
    print("Using Binance API for 4-hour price data")

    post_initial_tweet()

    initial_data = get_bitcoin_data()
    if initial_data is not None and initial_data:
        initial_price, initial_support, initial_resistance = find_simple_support_resistance(initial_data)
        if initial_price is not None and initial_support is not None and initial_resistance is not None:
            post_initial_tweet(initial_price, initial_support, initial_resistance)
        else:
            print("Could not determine initial price or levels for startup tweet.")
    else:
        print("Failed to fetch initial Bitcoin data for startup tweet.")


    last_tweet_time = time.time()
    last_tweeted_level = None

    while True:
        try:
            data = get_bitcoin_data()

            if data is not None and data:
                current_price, simple_support, simple_resistance = find_simple_support_resistance(data)

                if current_price is not None:
                    print(f"Current Bitcoin price: ${current_price:,.2f}")

                    current_time = time.time()

                    is_near_support = is_near_level(current_price, simple_support)
                    is_near_resistance = is_near_level(current_price, simple_resistance)

                    if (current_time - last_tweet_time) >= MIN_TWEET_INTERVAL:
                         last_tweeted_level = None

                         if is_near_support and last_tweeted_level != simple_support:
                             print(f"Price ${current_price:,.2f} is near simple support at ${simple_support:,.2f}. Posting tweet...")
                             post_tweet(current_price, simple_support, "support")
                             last_tweet_time = current_time
                             last_tweeted_level = simple_support
                         elif is_near_resistance and last_tweeted_level != simple_resistance:
                              print(f"Price ${current_price:,.2f} is near simple resistance at ${simple_resistance:,.2f}. Posting tweet...")
                              post_tweet(current_price, simple_resistance, "resistance")
                              last_tweet_time = current_time
                              last_tweeted_level = simple_resistance
                         else:
                             print("Price is near a level, but recently tweeted about this specific level, or no levels are near.")
                    else:
                        print(f"Minimum tweet interval not met. Waiting {MIN_TWEET_INTERVAL - (current_time - last_tweet_time):.0f} seconds.")


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
