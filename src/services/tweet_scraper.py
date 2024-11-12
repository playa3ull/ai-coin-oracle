from twikit import Client
from typing import List, Dict
import logging
from src.config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class TweetScraper:
    def __init__(self):
        self.client = Client(
            language='en-US',
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/130.0.0.0 Safari/537.36'
        )
        self._initialized = False

        self.default_queries = [
            "GameFi",
            "NFTGaming",
            "P2E",
            "BlockchainGaming",
            "CryptoGaming"
        ]
        self.monitor_username = settings.TWITTER_USERNAME
        self.processed_replies = set()

    async def initialize(self):
        """Initialize the Twitter client if not already initialized"""
        if not self._initialized:
            try:
                await self.client.login(
                    auth_info_1=settings.TWITTER_USERNAME,
                    auth_info_2=settings.TWITTER_EMAIL,
                    password=settings.TWITTER_PASSWORD,
                )
                self._initialized = True
                logger.info("Twitter client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {str(e)}")
                raise

    async def get_trending_tweets(
            self,
            queries: List[str] = None,
            limit: int = 5,
    ) -> List[Dict]:
        """
        Get trending tweets with essential information for retweets

        Args:
            queries: List of search queries
            limit: Maximum number of tweets per query

        Returns:
            List of tweets with essential data for retweeting
        """
        if not self._initialized:
            await self.initialize()

        search_queries = queries if queries else self.default_queries
        all_tweets = []

        try:
            for query in search_queries:
                tweets = await self.client.search_tweet(query, 'Top', limit)

                for tweet in tweets:
                    if tweet.retweeted_tweet:
                        continue

                    tweet_data = {
                        'tweet_id': tweet.id,
                        'tweet_text': tweet.text,
                        'author_id': tweet.user.id,
                        'author_name': tweet.user.name,
                        'author_username': tweet.user.screen_name,
                        'followers_count': tweet.user.followers_count,
                        'is_verified': tweet.user.verified or tweet.user.is_blue_verified,
                        'matched_query': query
                    }
                    all_tweets.append(tweet_data)

            # Remove duplicates based on tweet ID
            unique_tweets = {tweet['tweet_id']: tweet for tweet in all_tweets}
            sorted_tweets = sorted(
                unique_tweets.values(),
                key=lambda x: x['followers_count'],
                reverse=True
            )

            return sorted_tweets[:limit]

        except Exception as e:
            logger.error(f"Error fetching tweets: {str(e)}")
            raise

    async def check_new_replies(self, limit: int = 5) -> List[Dict]:
        """Check for new replies to recent tweets"""
        if not self._initialized:
            await self.initialize()

        try:
            # Get recent tweets
            user_id = await self.client.user_id()
            tweets = await self.client.get_user_tweets(
                user_id=user_id,
                tweet_type='Tweets',
                count=limit,
            )

            new_replies = []

            for tweet in tweets:
                print(f"Checking replies for tweet: {tweet.id}")
                replies = await self.search_replies_for_tweet(tweet.id)

                for reply in replies:
                    new_replies.append({
                        **reply,  # Include all reply data
                        'tweet_id': tweet.id,
                        'tweet_text': tweet.text
                    })

            return new_replies

        except Exception as e:
            logger.error(f"Error checking replies: {str(e)}")
            return []

    async def search_replies_for_tweet(self, tweet_id: str) -> List[Dict]:
        """Search for all replies to a specific tweet"""
        try:
            # Search for replies using conversation_id and in_reply_to filters
            query = f"conversation_id:{tweet_id}"
            replies = await self.client.search_tweet(
                query=query,
                product="Latest",
                count=20
            )

            reply_data = []
            if replies:
                for reply in replies:
                    if reply.id == tweet_id or reply.id in self.processed_replies:
                        continue

                    reply_data.append({
                        'reply_id': reply.id,
                        'reply_text': reply.text,
                        'reply_author': reply.user.screen_name,
                    })
                    self.processed_replies.add(reply.id)

            return reply_data

        except Exception as e:
            logger.error(f"Error searching replies for tweet {tweet_id}: {str(e)}")
            return []

    async def close(self):
        """Close the Twitter client connection"""
        if self._initialized:
            try:
                await self.client.logout()
                self._initialized = False
                logger.info("Twitter client closed successfully")
            except Exception as e:
                logger.error(f"Error closing Twitter client: {str(e)}")
                raise


async def main():
    """Test tweet and reply fetching"""
    scraper = TweetScraper()
    await scraper.initialize()

    replies = await scraper.check_new_replies(limit=3)
    for reply in replies:
        print(f"\n=== Reply ===")
        print(f"ID: {reply['reply_id']}")
        print(f"Text: {reply['reply_text']}")
        print(f"Author: {reply['reply_author']}")
        print(f"Original Tweet ID: {reply['tweet_id']}")
        print(f"Original Tweet Text: {reply['tweet_text']}")

    await scraper.close()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())