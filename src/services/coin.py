import aiohttp
import asyncio
from typing import List, Dict
import time
from src.config.settings import get_settings

settings = get_settings()


class CoinService:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = settings.COINGECKO_API_KEY
        self.last_request_time = 0
        self.min_request_interval = 1.5
        # self.categories = ['gaming', 'artificial-intelligence']
        self.categories = ['artificial-intelligence']

    async def _make_request(self, endpoint: str, params: dict = None) -> Dict:
        """
        Make a rate-limited API request to CoinGecko
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last_request)

        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{endpoint}"
                async with session.get(url, params=params, headers=headers) as response:
                    self.last_request_time = time.time()

                    if response.status == 429:
                        retry_after = int(response.headers.get('Retry-After', 60))
                        print(f"Rate limited. Waiting {retry_after} seconds...")
                        await asyncio.sleep(retry_after)
                        return await self._make_request(endpoint, params)

                    response.raise_for_status()
                    return await response.json()

        except aiohttp.ClientError as e:
            print(f"API request error: {str(e)}")
            raise

    async def get_trending_coins(self, limit: int = 10) -> List[Dict]:
        """
        Get trending coins from both gaming and AI categories
        """
        try:
            all_coins = []

            for category in self.categories:

                params = {
                    'vs_currency': 'usd',
                    'category': category,
                    'order': 'volume_desc',
                    'per_page': limit,
                    'page': 1,
                    'sparkline': 'false',
                    'price_change_percentage': '24h'
                }

                coins_data = await self._make_request("/coins/markets", params)

                trending_coins = [
                    {
                        'id': coin['id'],
                        'name': coin['name'],
                        'market_cap_rank': coin['market_cap_rank'],
                        'current_price': coin['current_price'],
                        'price_change_24h': coin['price_change_percentage_24h'],
                        'market_cap': coin['market_cap'],
                        'volume_24h': coin['total_volume'],
                        'category': category,
                    }
                    for coin in coins_data
                ]
                all_coins.extend(trending_coins)

            return all_coins

        except Exception as e:
            print(f"Error fetching trending gaming coins: {str(e)}")
            raise

    async def get_coins_summary(self) -> Dict:
        """
        Get a summary of gaming and AI category coins including market metrics
        """
        try:
            summaries = {}

            for category in self.categories:
                params = {'vs_currency': 'usd'}
                data = await self._make_request(f"/coins/categories/{category}", params)

                summaries[category] = {
                    'market_cap': data.get('market_cap', 0),
                    'total_volume': data.get('volume_24h', 0),
                    'market_cap_change_24h': data.get('market_cap_change_24h', 0),
                    'top_coins': data.get('top_3_coins_id', [])
                }

            return summaries

        except Exception as e:
            print(f"Error fetching gaming category summary: {str(e)}")
            raise
