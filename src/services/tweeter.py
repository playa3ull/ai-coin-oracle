import tweepy
import os
from dotenv import load_dotenv

load_dotenv()


class TweetPoster:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )

    def post_tweet(self, text: str) -> str:
        try:
            if len(text) > 280:
                text = text[:277] + "..."

            response = self.client.create_tweet(text=text)
            if response.data:
                return response.data['id']
            return None
        except Exception as e:
            print(f"Error posting tweet: {e}")
            return None


if __name__ == '__main__':
    poster = TweetPoster()
    poster.post_tweet("Hello, Twitter!")