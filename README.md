# AI Coin Oracle 🪙

An AI-powered Twitter bot that generates and posts insights about trending GameFi cryptocurrencies using market data and GPT-4.

## Quick Start 🚀

### Prerequisites
- Docker and Docker Compose
- Twitter Developer Account
- CoinGecko API Key
- OpenAI API Key

### Setup

1. Clone the repository
```bash
git clone <repository-url>
cd AI_Coin_Oracle
```

2. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```env
OPENAI_API_KEY=your_openai_key
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
COINGECKO_API_KEY=your_coingecko_key

#Twitter Account (retweeting)
TWITTER_USERNAME=your_twitter_username
TWITTER_EMAIL=your_twitter_email
TWITTER_PASSWORD=your_twitter_password

# Optional
ENABLE_IMAGE_GENERATION=true 
OPENAI_MODEL=your_openai_model 
```

3. Build and run with Docker
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### Health Check
```bash
curl http://localhost:8000/
```

Get the current schedule times:
```bash
curl http://localhost:8000/get-schedule-times
```

### Basic Usage

1. Generate and post a tweet:
```bash
curl -X POST http://localhost:8000/generate-tweet
```

2. Schedule a test tweet (30 seconds from now):
```bash
curl -X POST http://localhost:8000/schedule-test
```

3. Schedule a custom tweet:
```bash
curl -X POST "http://localhost:8000/schedule-tweet?time=15:00"
```

4. Retweet a tweet:
```bash
curl -X POST "http://localhost:8000/generate-retweet"
```

5. Generate a comment to trending tweet:
```bash
curl -X POST "http://localhost:8000/generate-comment"
```


## Project Structure 📁
```
AI_Coin_Oracle/
├── config/
│   └── settings.py
├── src/
│   ├── services/
│   │   ├── coin.py         # CoinGecko API integration
│   │   ├── llm.py          # GPT-4 integration
│   │   ├── scheduler.py    # Tweet scheduling
│   │   ├── tweet_service.py # Tweet generation
│   │   ├── tweet_scraper.py # Trending tweets scraping
│   │   ├── image_generator.py # AI image generation
│   │   └── tweeter.py      # Twitter API integration
│   └── __init__.py
├── tests/
│   └── test.py
├── docker-compose.yml
├── Dockerfile
├── main.py
├── requirements.txt
└── README.md
```




