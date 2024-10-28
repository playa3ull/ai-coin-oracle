from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.services.coin import CoinService
from src.services.tweeter import TweetPoster
from src.services.tweet_service import TweetService
from src.services.llm import LLMService
from src.services.scheduler import TweetScheduler
import uvicorn
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

app = FastAPI()

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
tweet_service = TweetService(coin_service, llm_service, tweet_poster)
scheduler = TweetScheduler(tweet_service)


class TweetResponse(BaseModel):
    success: bool
    message: str
    tweet_id: str = None


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
    """Schedule a tweet for 1 minutes from now"""
    test_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
    try:
        scheduler.schedule_tweet(test_time)
        return {"message": f"Test tweet scheduled for {test_time}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-tweet", response_model=TweetResponse)
async def generate_and_post_tweet():
    return await tweet_service.generate_and_post_tweet()


@app.on_event("startup")
async def start_scheduler():
    scheduler.start()


@app.on_event("shutdown")
async def stop_scheduler():
    scheduler.stop()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
