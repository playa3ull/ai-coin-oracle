from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import logging
from src.config.settings import get_settings
import pytz

settings = get_settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TweetScheduler:
    def __init__(self, tweet_service):
        self.local_tz = pytz.timezone(settings.LOCAL_TIMEZONE)
        self.target_tz = pytz.timezone(settings.TARGET_TIMEZONE)
        self.scheduler = AsyncIOScheduler(timezone=self.target_tz)
        self.tweet_service = tweet_service
        self.schedule_times = settings.SCHEDULE_TIMES

    def _convert_to_target_time(self, time_str: str) -> datetime:
        """
        Convert local time string to target timezone datetime

        Args:
            time_str: Time in HH:MM format
        Returns:
            datetime: Converted datetime in target timezone
        """
        try:
            hour, minute = map(int, time_str.split(":"))
            local_now = datetime.now(self.local_tz)
            local_time = local_now.replace(
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0
            )

            # If the time has already passed today, schedule for tomorrow
            if local_time <= local_now:
                local_time = local_time + timedelta(days=1)

            target_time = local_time.astimezone(self.target_tz)
            return target_time

        except ValueError:
            raise ValueError("Invalid time format. Please use HH:MM format (e.g., 14:30)")

    def schedule_tweet(self, time_str: str) -> None:
        """Schedule a tweet for a specific time"""
        try:
            target_time = self._convert_to_target_time(time_str)

            self.scheduler.add_job(
                self.tweet_service.generate_and_post_tweet,
                'date',
                run_date=target_time,
                id=f'tweet_{time_str}_{target_time.timestamp()}'
            )
            logger.info(f"Tweet scheduled for {time_str}, target time: {target_time}")

        except Exception as e:
            logger.error(f"Error scheduling tweet: {str(e)}")
            raise

    def _schedule_daily_tweet(self, time_str: str) -> None:
        """Schedule a recurring daily tweet"""
        try:
            hour, minute = map(int, time_str.split(":"))
            self.scheduler.add_job(
                self.tweet_service.generate_and_post_tweet,
                'cron',
                hour=hour,
                minute=minute,
                timezone=self.target_tz,
                id=f'daily_tweet_{time_str}'
            )
        except Exception as e:
            print(f"Failed to schedule daily tweet at {time_str}: {str(e)}")

    def get_health_status(self) -> dict:
        """Get scheduler health status"""
        return {
            "is_running": self.scheduler.running,
            "job_count": len(self.scheduler.get_jobs()),
            "next_run_time": str(self.scheduler.get_jobs()[0].next_run_time) if self.scheduler.get_jobs() else None
        }

    def start(self) -> None:
        """Start the scheduler with configured times"""
        try:
            for time in self.schedule_times:
                self.schedule_tweet(time)

            self.scheduler.start()
            logger.info("Scheduler started successfully")

        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
            raise

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
