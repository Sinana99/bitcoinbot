import os
import time
import tweepy
import requests
from dotenv import load_dotenv

load_dotenv()


TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# --- Fear & Greed Index API Endpoint ---
# API documentation: https://alternative.me/crypto/fear-and-greed-index/
FG_INDEX_API_URL = "https://api.alternative.me/fng/"


CHECK_INTERVAL_SECONDS = 6 * 3600 # Check and tweet four times a day

def get_fear_greed_index():
    """Fetches the current Crypto Fear & Greed Index value."""
    try:
  
        response = requests.get(FG_INDEX_API_URL)
      
        data = response.json()

    
        index_value = int(data['data'][0]['value'])
        index_classification = data['data'][0]['value_classification']

        print(f"Fetched Fear & Greed Index: {index_value} ({index_classification})")
        return index_value, index_classification

    except requests.exceptions.RequestException as e:
      
        print(f"Error fetching Fear & Greed Index: {e}")
        return None, None
    except (KeyError, IndexError, ValueError) as e:
        
        print(f"Error parsing Fear & Greed Index data: {e}")
        return None, None
    except Exception as e:
        
        print(f"An unexpected error occurred while fetching index: {e}")
        return None, None


def post_fear_greed_tweet(index_value, index_classification):
    """Posts the Fear & Greed Index value to Twitter."""
    try:
      
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )

       
        emoji = "😨" if "Fear" in index_classification else ("🤩" if "Greed" in index_classification else "��")
        emoji2 = "🚨"

        
        tweet_text = f"{emoji2} Crypto Fear & Greed Index Update {emoji2}\n\n" \
                     f"Current Index: {index_value} {emoji} ({index_classification})\n\n" \
                     f"#CryptoSentiment #Bitcoin #Crypto #FearAndGreedIndex" # Relevant hashtags

      
        response = client.create_tweet(text=tweet_text)
        print(f"Successfully posted tweet: {tweet_text}")

    except tweepy.TweepyException as e:
        
        print(f"Twitter API Error posting tweet: {e}")
    except Exception as e:
      
        print(f"Error posting tweet: {e}")


def main():
    """Main function to run the Fear & Greed Index bot."""
    print("Starting Crypto Fear & Greed Index Bot...")

  
    last_tweet_time = 0

   
    while True:
        try:
            current_time = time.time()

          
            if (current_time - last_tweet_time) >= CHECK_INTERVAL_SECONDS:
          
                index_value, index_classification = get_fear_greed_index()

              
                if index_value is not None and index_classification is not None:
                  
                    post_fear_greed_tweet(index_value, index_classification)
                
                    last_tweet_time = current_time
                else:
              
                    print("Failed to get Fear & Greed Index data.")

            else:
              
                time_remaining = CHECK_INTERVAL_SECONDS - (current_time - last_tweet_time)
                print(f"Next check in {time_remaining:.0f} seconds.")


        except Exception as e:
       
            print(f"Error in main loop: {e}")
            
            print("Waiting for 5 minutes before retrying after error...")
            time.sleep(300)


        time.sleep(3600) 


if __name__ == "__main__":
   
    main()
