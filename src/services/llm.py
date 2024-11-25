from llama_index.llms.openai import OpenAI
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.llms import ChatMessage
from src.config.settings import get_settings
from typing import List, Dict
import json
import random
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

settings = get_settings()
load_dotenv()


class LLMService:
    def __init__(self):
        self.key = settings.OPENAI_API_KEY.strip()
        self.llm = OpenAI(model=settings.OPENAI_MODEL, api_key=self.key, temperature=0.8, max_tokens=110)
        self.memory = ChatMemoryBuffer.from_defaults(token_limit=2048)

    async def generate_tweet(self, trending_coins: List[Dict], market_summary: Dict = None) -> str:
        """
        Generate a tweet about trending gaming and AI coins

        Args:
            trending_coins: List of trending gaming coins with detailed metrics
            market_summary: Gaming market overview and metrics
        """

        coins_by_category = {}
        for coin in trending_coins:
            category = coin['category']
            if category not in coins_by_category:
                coins_by_category[category] = []
            coins_by_category[category].append({
                "name": coin["name"],
                "price": f"${coin['current_price']:.6f}" if coin[
                                                                'current_price'] < 0.01 else f"${coin['current_price']:.2f}",
                "change_24h": f"{coin['price_change_24h']:.1f}%",
                "volume": f"${coin['volume_24h']:,.0f}",
                "market_cap_rank": coin["market_cap_rank"]
            })

        market_context = {
            category: {
                "total_market_cap": f"${summary['market_cap']:,.0f}",
                "total_volume": f"${summary['total_volume']:,.0f}",
                "market_cap_change": f"{summary['market_cap_change_24h']:.1f}%",
                "top_coins": summary["top_coins"]
            }
            for category, summary in market_summary.items()
        }

        context = {
            "trending_coins": coins_by_category,
            "market_overview": market_context if market_summary else None
        }

        tweet_styles = [
            "Breaking news style",
            "Market insight",
            "Community focus",
            "Trend analysis"
        ]

        hook_patterns = [
            "Breaking: {coin} just...",
            "🚨 {coin} Alert:",
            "Trending Now:",
            "Market Move:",
            "Who spotted {trend}?",
            "Tech Update:",
            "Whale Alert:",
            "New Milestone:"
        ]

        chat_history = self.memory.get()
        recent_tweets = "\n".join([
            f"- {msg.content}"
            for msg in chat_history
            if msg.role == "assistant"
        ])

        prompt = f"""
            You are a crypto expert writing viral tweets about GameFi and AI tokens.
            Market data: {json.dumps(context, indent=2)}
            
            Recent tweets (Avoid similar content):
            {recent_tweets}
            
            Hook examples:
            {json.dumps(hook_patterns, indent=2)} 

            Core Requirements:
            - Length flexibility (Max 260 chars)
            - Focus on significant market movements or interesting data points
            - Include relevant emojis and hashtags based on category
            - Add sense of humor or curiosity if possible
            - Avoid same data points or coin in recent tweets
            - Avoid using too many numbers
            - No formatting (bold/italic)
            
            Choose a style for the tweet:{', '.join(tweet_styles)}

            Write an tweet that crypto enthusiasts want to engage with:
            """

        response = await self.llm.acomplete(prompt)
        tweet = response.text.strip()

        if len(tweet) > 275:
            tweet = tweet[:272] + "..."

        self.memory.put(ChatMessage(role="assistant", content=tweet))

        return tweet

    async def generate_social_response(self, trending_tweets: List[Dict], response_type: str) -> Dict:
        """
        Select a tweet from trending tweets and generate a response for retweeting or commenting

        Args:
            trending_tweets: List of trending tweets with their metadata
            response_type: Either 'retweet' or 'comment'

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

        max_length = 100 if response_type == 'retweet' else 180

        prompt = f"""
                    You are a knowledgeable crypto gaming expert managing a Twitter account. 
                    Review these trending tweets and select ONE to {response_type} to:

                    {tweets_context}

                    Selection tips:
                    - Pick tweets about game features, updates, or community topics
                    - Prefer verified accounts or engaging discussions
                    - Look for topics you can add value to

                    Writing style:
                    - Keep it under {max_length} characters
                    - Be genuine and conversational
                    - Use light humor when it fits naturally
                    - Add your unique gaming perspective

                    Return your response as JSON:
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

    async def generate_retweet(self, trending_tweets: List[Dict]) -> Dict:
        return await self.generate_social_response(trending_tweets, 'retweet')

    async def generate_comment(self, trending_tweets: List[Dict]) -> Dict:
        return await self.generate_social_response(trending_tweets, 'comment')

    def _format_tweet_url(self, tweet_id: str) -> str:
        """Format a tweet URL from tweet ID"""
        return f"https://twitter.com/i/web/status/{tweet_id}"


# if __name__ == '__main__':
#     import asyncio
#     from src.services.tweet_scraper import TweetScraper
#
#     tweet_scraper = TweetScraper()
#     tweets = asyncio.run(tweet_scraper.get_trending_tweets(limit=5))
#
#     llm = LLMService()
#     response = asyncio.run(llm.generate_retweet(tweets))
#     print(response)
