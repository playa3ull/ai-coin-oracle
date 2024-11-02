from fastapi import HTTPException
import logging
from typing import Optional, Dict, Any
import os
from src.config.settings import get_settings

settings = get_settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TweetService:
    def __init__(self, coin_service, llm_service, tweet_poster, image_generator):
        self.coin_service = coin_service
        self.llm_service = llm_service
        self.tweet_poster = tweet_poster
        self.image_generator = image_generator
        self.use_images = settings.ENABLE_IMAGE_GENERATION

    async def generate_and_post_tweet(self, force_image: bool = False) -> Dict[str, Any]:
        """
        Generate and post a tweet with optional image generation

        Args:
            force_image: Override environment setting and force image generation

        Returns:
            Dict containing response data
        """
        image_path = None
        try:
            # Get market data
            trending_coins = await self.coin_service.get_trending_gaming_coins()
            if not trending_coins:
                raise HTTPException(status_code=404, detail="No trending gaming coins found")

            market_summary = await self.coin_service.get_gaming_coins_summary()

            # Generate tweet content
            tweet_content = await self.llm_service.generate_tweet(trending_coins, market_summary)

            # Generate image if enabled
            if force_image or self.use_images:
                try:
                    image_path = await self.image_generator.generate_image(tweet_content)
                except Exception as e:
                    logger.error(f"Image generation failed: {str(e)}")
                    image_path = None

            tweet_id = self.tweet_poster.post_tweet(tweet_content, image_path)

            if tweet_id:
                return {
                    "success": True,
                    "message": "Tweet posted successfully",
                    "tweet_id": str(tweet_id),
                    "generated_image": bool(image_path)
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to post tweet")

        except Exception as e:
            logger.error(f"Error in tweet generation/posting: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

        finally:
            if image_path:
                await self.image_generator.cleanup_image(image_path)

        # return response
