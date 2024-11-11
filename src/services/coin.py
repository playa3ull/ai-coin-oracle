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

    # In src/services/coin.py
    async def _make_request(self, endpoint: str, params: dict = None) -> Dict:
        """
        Make a rate-limited API request to CoinGecko
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last_request)

        # Simplified, reliable headers
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",  # Simple compression without brotli
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{endpoint}"
                print(f"Making request to {url}")
                print(f"With headers: {headers}")

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

    async def get_trending_gaming_coins(self, limit: int = 10) -> List[Dict]:
        """
        Get trending gaming coins using the coins/markets endpoint with gaming category
        """
        try:
            # Get gaming coins sorted by market cap
            params = {
                'vs_currency': 'usd',
                'category': 'gaming',
                'order': 'volume_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '24h'
            }

            coins_data = await self._make_request("/coins/markets", params)

            # Format the response
            trending_coins = [
                {
                    'id': coin['id'],
                    'name': coin['name'],
                    'symbol': coin['symbol'].upper(),
                    'market_cap_rank': coin['market_cap_rank'],
                    'current_price': coin['current_price'],
                    'price_change_24h': coin['price_change_percentage_24h'],
                    'market_cap': coin['market_cap'],
                    'volume_24h': coin['total_volume'],
                    'image': coin['image'],
                    'last_updated': coin['last_updated']
                }
                for coin in coins_data
            ]

            return trending_coins

        except Exception as e:
            print(f"Error fetching trending gaming coins: {str(e)}")
            raise

    async def get_gaming_coins_summary(self) -> Dict:
        """
        Get a summary of gaming category coins including market metrics
        """
        try:
            params = {'vs_currency': 'usd'}
            category_data = await self._make_request("/coins/categories/gaming", params)

            return {
                'market_cap': category_data.get('market_cap', 0),
                'total_volume': category_data.get('volume_24h', 0),
                'market_cap_change_24h': category_data.get('market_cap_change_24h', 0),
                'volume_change_24h': category_data.get('volume_change_24h', 0)
            }

        except Exception as e:
            print(f"Error fetching gaming category summary: {str(e)}")
            raise

# Example usage
# async def main():
#     coin_service = CoinService()
#
#     # Get trending gaming coins
#     trending = await coin_service.get_trending_gaming_coins(limit=10)
#     print("\nTop 10 Trending Gaming Coins (by 24h volume):")
#     for coin in trending:
#         print(f"{coin['name']} ({coin['symbol']}):")
#         print(f"  Price: ${coin['current_price']:.4f}")
#         print(f"  24h Change: {coin['price_change_24h']:.2f}%")
#         print(f"  24h Volume: ${coin['volume_24h']:,.2f}")
#         print()
#
#     # Get gaming category summary
#     summary = await coin_service.get_gaming_coins_summary()
#     print("\nGaming Coins Category Summary:")
#     print(f"Total Market Cap: ${summary['market_cap']:,.2f}")
#     print(f"24h Volume: ${summary['total_volume']:,.2f}")
#     print(f"Market Cap Change 24h: {summary['market_cap_change_24h']:.2f}%")
#     print(f"Volume Change 24h: {summary['volume_change_24h']:.2f}%")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
