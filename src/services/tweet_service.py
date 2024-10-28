from fastapi import HTTPException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TweetService:
    def __init__(self, coin_service, llm_service, tweet_poster):
        self.coin_service = coin_service
        self.llm_service = llm_service
        self.tweet_poster = tweet_poster

    async def generate_and_post_tweet(self, test_mode=False):
        """Generate and post a tweet based on market data"""
        try:
            # Get market data
            trending_coins = await self.coin_service.get_trending_gaming_coins()
            if not trending_coins:
                raise HTTPException(status_code=404, detail="No trending gaming coins found")

            market_summary = await self.coin_service.get_gaming_coins_summary()

            # Generate tweet content
            tweet_content = await self.llm_service.generate_tweet(trending_coins, market_summary)

            if test_mode:
                logger.info(f"Test Mode - Tweet Content: {tweet_content}")
                return {
                    "success": True,
                    "message": "Test tweet generated",
                    "content": tweet_content
                }

            # Post tweet
            tweet_id = self.tweet_poster.post_tweet(tweet_content)

            if tweet_id:
                return {
                    "success": True,
                    "message": "Tweet posted successfully",
                    "tweet_id": str(tweet_id)
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to post tweet")

        except Exception as e:
            logger.error(f"Error in tweet generation/posting: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))