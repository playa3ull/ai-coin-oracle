from llama_index.llms.openai import OpenAI
from src.services.tweeter import TweetPoster
from typing import List, Dict
import json
import asyncio
import random
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    def __init__(self):
        self.llm = OpenAI(model="gpt-4o-mini", temperature=0.8, max_tokens=110)

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
            - Must be under 280 characters
            - Focus on significant market movements or interesting volume changes
            - Add gaming-related context when relevant
            - Include relevant emojis and hashtags
            - Natural, conversational tone
            - Avoid price predictions or financial advice
            - No italics or bold text

            Write a tweet that crypto gaming enthusiasts would want to engage with.
            Make it feel natural and exciting, not like a generic market update.
            
            Choose a style for the tweet:{tweet_styles}

            Tweet:
            """

        # selected_style = random.choice(tweet_styles)
        # prompt += f"\nStyle: {selected_style}"

        response = await self.llm.acomplete(prompt)
        tweet = response.text.strip()

        if len(tweet) > 280:
            return tweet[:277] + "..."
        else:
            return tweet


# Example usage
async def main():
    llm_service = LLMService()

    # Sample data for testing
    trending_coins = [
        {
            'name': 'Axie Infinity',
            'symbol': 'AXS',
            'current_price': 4.91,
            'price_change_24h': -4.13,
            'volume_24h': 75947295,
            'market_cap_rank': 106
        },
        {
            'name': 'The Sandbox',
            'symbol': 'SAND',
            'current_price': 0.3248,
            'price_change_24h': 2.5,
            'volume_24h': 50123456,
            'market_cap_rank': 98
        }
    ]

    market_summary = {
        'market_cap': 15000000000,
        'total_volume': 2000000000,
        'market_cap_change_24h': 5.2,
        'volume_change_24h': 15.7
    }

    tweet = await llm_service.generate_tweet(trending_coins, market_summary)
    return tweet


if __name__ == '__main__':
    tweet = asyncio.run(main())
    if len(tweet) > 280:
        print(f"Tweet length: {len(tweet)}")
        tweet = tweet[:277] + "..."
        print(len(tweet))
    tweet_poster = TweetPoster()
    tweet_poster.post_tweet(tweet)
