from llama_index.llms.openai import OpenAI
from src.config.settings import get_settings
from typing import List, Dict
import json
import asyncio
import random
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

settings = get_settings()
load_dotenv()


class LLMService:
    def __init__(self):
        self.llm = OpenAI(model=settings.OPENAI_MODEL, temperature=0.8, max_tokens=110)

    async def generate_tweet(self, trending_coins: List[Dict], market_summary: Dict = None) -> str:
        """
        Generate a tweet about trending gaming coins

        Args:
            trending_coins: List of trending gaming coins with detailed metrics
            market_summary: Gaming market overview and metrics
        """

        market_context = {
            "total_market_cap": f"${market_summary['market_cap']:,.0f}" if market_summary else None,
            "total_volume": f"${market_summary['total_volume']:,.0f}" if market_summary else None,
            "market_cap_change": f"{market_summary['market_cap_change_24h']:.1f}%" if market_summary else None,
            "volume_change": f"{market_summary['volume_change_24h']:.1f}%" if market_summary else None
        }

        context = {
            "trending_coins": [
                {
                    "name": coin["name"],
                    "symbol": coin["symbol"],
                    "price": f"${coin['current_price']:.6f}" if coin[
                                                                    'current_price'] < 0.01 else f"${coin['current_price']:.2f}",
                    "change_24h": f"{coin['price_change_24h']:.1f}%",
                    "volume": f"${coin['volume_24h']:,.0f}",
                    "market_cap_rank": coin["market_cap_rank"]
                }
                for coin in trending_coins[:3]
            ],
            "market_overview": market_context if market_summary else None
        }

        tweet_styles = [
            "Breaking news style",
            "Casual observation",
            "Market insight",
            "Gaming community focus",
            "Trend analysis"
        ]

        prompt = f"""
            You are a crypto gaming expert writing viral tweets about GameFi tokens and gaming crypto trends.
            Market context: {json.dumps(context, indent=2)}

            Core Requirements:
            - Must be under 275 characters
            - Focus on significant market movements or interesting volume changes
            - Add gaming-related context when relevant
            - Include relevant emojis and hashtags
            - Natural, conversational tone
            - Avoid price predictions or financial advice
            - No italics or bold text

            Write a tweet that crypto gaming enthusiasts would want to engage with.
            Make it feel natural and exciting, not like a generic market update.
            
            Choose a style for the tweet:{', '.join(tweet_styles)}

            Tweet:
            """

        response = await self.llm.acomplete(prompt)
        tweet = response.text.strip()

        if len(tweet) > 275:
            tweet = tweet[:272] + "..."

        return tweet

    async def generate_retweet(self, trending_tweets: List[Dict]) -> Dict:
        """
        Select a tweet from trending tweets and generate a response

        Args:
            trending_tweets: List of trending tweets with their metadata

        Returns:
            Dict containing selected tweet and generated response
        """
        if trending_tweets:
            tweets_context = json.dumps([{
                'text': t['tweet_text'],
                'author': t['author_username'],
                'followers': t['followers_count'],
                'is_verified': t['is_verified'],
                'query': t['matched_query']
            } for t in trending_tweets], indent=2)

        prompt = f"""
                    You are a knowledgeable crypto gaming expert managing a Twitter account. 
                    Review these trending GameFi tweets and select ONE to respond to:

                    {tweets_context}

                    Requirements for selection:
                    - Choose tweet with substantial discussion potential
                    - Prefer verified accounts or those with more followers
                    - Avoid controversial or negative content
                    - Prioritize tweets about gaming mechanics, new features, or market analysis

                    Requirements for response:
                    - Must be under 100 characters (to leave room for quote tweet)
                    - Add value through insight, analysis, or relevant context
                    - Be engaging but professional
                    - Include 1-2 relevant emojis
                    - Don't just agree or praise - add substance
                    - No price predictions or financial advice
                    - Keep the tone optimistic but grounded

                    First select the best tweet to respond to, then generate a response.
                    Return your selection and response in this JSON format:
                    {{"selected_index": <index of chosen tweet>, "response": "<your response>"}}
                """

        try:
            response = await self.llm.acomplete(prompt)
            result = json.loads(response.text.strip())

            # Get the full tweet data for the selected tweet
            selected_tweet = trending_tweets[result['selected_index']]

            return {
                'tweet': selected_tweet,
                'response': result['response'].strip()
            }

        except (json.JSONDecodeError, IndexError, KeyError) as e:
            logger.error(f"Error processing LLM response: {str(e)}")
            # Fallback to random selection with generic response
            selected_tweet = random.choice(trending_tweets)
            return {
                'tweet': selected_tweet,
                'response': "Interesting perspective on GameFi! 🎮 The gaming ecosystem keeps evolving. #GameFi #P2E"
            }
        except Exception as e:
            logger.error(f"Unexpected error in response generation: {str(e)}")
            raise

    def _format_tweet_url(self, tweet_id: str) -> str:
        """Format a tweet URL from tweet ID"""
        return f"https://twitter.com/i/web/status/{tweet_id}"




if __name__ == '__main__':
    from src.services.tweet_scraper import TweetScraper
    tweet_scraper = TweetScraper()
    tweets = asyncio.run(tweet_scraper.get_trending_tweets(limit=5))

    llm = LLMService()
    response = asyncio.run(llm.generate_retweet(tweets))
    print(response)
