from twikit import Client
from typing import List, Dict
import logging
from src.config.settings import get_settings

settings = get_settings()
logging.basicConfig(level=logging.INFO)
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
            search_type: str = 'Top'
    ) -> List[Dict]:
        """
        Get trending tweets with essential information for retweets

        Args:
            queries: List of search queries
            limit: Maximum number of tweets per query
            search_type: Type of search ('Top', 'Latest', 'People', 'Photos', 'Videos')

        Returns:
            List of tweets with essential data for retweeting
        """
        if not self._initialized:
            await self.initialize()

        search_queries = queries if queries else self.default_queries
        all_tweets = []

        try:
            for query in search_queries:
                tweets = await self.client.search_tweet(query, search_type, limit)

                for tweet in tweets:
                    # Skip if it's already a retweet
                    if tweet.retweeted_tweet:
                        continue

                    # Extract only essential information
                    tweet_data = {
                        # Tweet info needed for retweeting
                        'tweet_id': tweet.id,
                        'tweet_text': tweet.text,

                        # Author info needed for context/response generation
                        'author_id': tweet.user.id,
                        'author_name': tweet.user.name,
                        'author_username': tweet.user.screen_name,

                        # Engagement metrics for filtering/sorting
                        'followers_count': tweet.user.followers_count,
                        'is_verified': tweet.user.verified or tweet.user.is_blue_verified,

                        # Additional context for response generation
                        'matched_query': query
                    }
                    all_tweets.append(tweet_data)

            # Remove duplicates based on tweet ID
            unique_tweets = {tweet['tweet_id']: tweet for tweet in all_tweets}

            # Sort by follower count as a basic relevance metric
            sorted_tweets = sorted(
                unique_tweets.values(),
                key=lambda x: x['followers_count'],
                reverse=True
            )

            return sorted_tweets[:limit]

        except Exception as e:
            logger.error(f"Error fetching tweets: {str(e)}")
            raise

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


if __name__ == '__main__':
    import asyncio
    scraper = TweetScraper()
    tweets = asyncio.run(scraper.get_trending_tweets())
    print(tweets)
    scraper.close()