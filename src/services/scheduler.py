from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TweetScheduler:
    def __init__(self, tweet_service):
        self.scheduler = AsyncIOScheduler()
        self.tweet_service = tweet_service

        # Default schedule times
        self.schedule_times = [
            "10:00",  # Morning
            "15:00",  # Afternoon
            "20:00"  # Evening
        ]

    def schedule_tweet(self, time_str: str):
        """Schedule a tweet for a specific time"""
        try:
            hour, minute = map(int, time_str.split(":"))

            self.scheduler.add_job(
                self.tweet_service.generate_and_post_tweet,
                'cron',
                hour=hour,
                minute=minute,
                id=f'tweet_{time_str}'
            )
            logger.info(f"Tweet scheduled for {time_str}")

        except Exception as e:
            logger.error(f"Error scheduling tweet: {str(e)}")
            raise

    def start(self):
        """Start the scheduler with configured times"""
        try:
            # Schedule all configured times
            for time in self.schedule_times:
                self.schedule_tweet(time)

            self.scheduler.start()
            logger.info("Scheduler started successfully")

        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
            raise

    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
            raise