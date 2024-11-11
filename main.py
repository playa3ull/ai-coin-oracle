from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.config.settings import get_settings
from src.services.coin import CoinService
from src.services.tweeter import TweetPoster
from src.services.tweet_service import TweetService
from src.services.image_generator import ImageGenerator
from src.services.tweet_scraper import TweetScraper
from src.services.llm import LLMService
from src.services.scheduler import TweetScheduler
import uvicorn

settings = get_settings()

app = FastAPI(title="AI Coin Oracle")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
coin_service = CoinService()
tweet_poster = TweetPoster()
llm_service = LLMService()
image_generator = ImageGenerator()
tweet_scraper = TweetScraper()
tweet_service = TweetService(coin_service, llm_service, tweet_poster, image_generator, tweet_scraper)
scheduler = TweetScheduler(tweet_service)


class TweetResponse(BaseModel):
    success: bool
    message: str
    tweet_id: str = None


class RetweetResponse(BaseModel):
    success: bool
    message: str
    tweet_id: str = None
    original_tweet: dict = None
    response: str = None


@app.get("/")
async def root():
    return {"message": "Gaming Coins Twitter Bot API"}


@app.post("/schedule-tweet")
async def schedule_custom_tweet(time: str):
    """Schedule a tweet for a specific time (HH:MM format)"""
    try:
        scheduler.schedule_tweet(time)
        return {"message": f"Tweet scheduled for {time}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule-test")
async def schedule_test():
    """Schedule a tweet for 30 seconds from now"""
    test_time = (datetime.now() + timedelta(seconds=30)).strftime("%H:%M")
    try:
        scheduler.schedule_tweet(test_time)
        return {"message": f"Test tweet scheduled for {test_time}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-tweet", response_model=TweetResponse)
async def generate_and_post_tweet(force_image: bool = False):
    return await tweet_service.generate_and_post_tweet(force_image)


@app.post("/generate-retweet", response_model=RetweetResponse)
async def generate_and_post_retweet():
    return await tweet_service.generate_and_post_retweet()


@app.on_event("startup")
async def start_scheduler():
    scheduler.start()


@app.on_event("shutdown")
async def stop_scheduler():
    scheduler.stop()


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
