import tweepy
from src.config.settings import get_settings
import logging
import os
from typing import Optional

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TweetPoster:
    def __init__(self):

        self.client = tweepy.Client(
            consumer_key=settings.TWITTER_API_KEY.strip(),
            consumer_secret=settings.TWITTER_API_SECRET.strip(),
            access_token=settings.TWITTER_ACCESS_TOKEN.strip(),
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET.strip()
        )
        print('sssssss')
        print(self.client.get_me())
        print(settings.TWITTER_API_KEY.strip(), settings.TWITTER_API_SECRET.strip(), settings.TWITTER_ACCESS_TOKEN.strip(), settings.TWITTER_ACCESS_TOKEN_SECRET.strip())
        print('ssssss')

        auth = tweepy.OAuth1UserHandler(
            settings.TWITTER_API_KEY.strip(),
            settings.TWITTER_API_SECRET.strip(),
            settings.TWITTER_ACCESS_TOKEN.strip(),
            settings.TWITTER_ACCESS_TOKEN_SECRET.strip()
        )
        self.api = tweepy.API(auth)

    def post_tweet(self, text: str, media_path: Optional[str] = None) -> str:
        """
        Post a tweet with optional media

        Args:
            text: Tweet text content
            media_path: Optional path to media file

        Returns:
            str: Tweet ID if successful, None otherwise
        """
        try:
            if len(text) > 280:
                text = text[:277] + "..."

            media_ids = []
            if media_path and os.path.exists(media_path):
                # Upload media using v1 API
                media = self.api.media_upload(filename=media_path)
                media_ids.append(media.media_id)

            # Post tweet with optional media
            response = self.client.create_tweet(
                text=text,
                media_ids=media_ids if media_ids else None
            )

            return response.data['id'] if response.data else None

        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return None

    def retweet_with_comment(self, tweet_id: str, comment: str) -> str:
        """
        Retweet a tweet with a comment (quote tweet)

        Args:
            tweet_id: ID of the tweet to retweet
            comment: Comment to add to the retweet

        Returns:
            str: New tweet ID if successful, None otherwise
        """
        try:
            if len(comment) > 280:
                comment = comment[:277] + "..."

            # Create quote tweet
            response = self.client.create_tweet(
                text=comment,
                quote_tweet_id=tweet_id
            )

            return response.data['id'] if response.data else None

        except Exception as e:
            logger.error(f"Error creating quote tweet: {str(e)}")
            return None

    def post_comment(self, tweet_id: str, comment: str) -> str:
        """
        Post a comment to an existing tweet

        Args:
            tweet_id: ID of the tweet to comment on
            comment: Comment text

        Returns:
            str: New tweet ID if successful, None otherwise
        """
        try:
            if len(comment) > 270:
                comment = comment[:267] + "..."

            # Post comment
            response = self.client.create_tweet(
                text=comment,
                in_reply_to_tweet_id=tweet_id
            )

            return response.data['id'] if response.data else None

        except Exception as e:
            logger.error(f"Error posting comment: {str(e)}")
            return None

# if __name__ == '__main__':
#     poster = TweetPoster()
#     poster.retweet_with_comment('1747302774683910652','Exciting insights!')
