from openai import AsyncOpenAI
import aiohttp
import random
import os
import logging
from typing import Optional
import asyncio
from src.config.settings import get_settings

settings = get_settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageGenerator:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.temp_dir = "/tmp/crypto_images"
        self.styles = [
            'pixel-art',
            'cyberpunk',
            'cartoon',
            'vaporwave',
            'abstract',
            'isometric',
            'tech_blueprint',
        ]

    async def generate_image(self, tweet_text: str) -> Optional[str]:
        """
        Generate an image directly from tweet text using DALL-E
        """
        try:
            selected_style = random.choice(self.styles)

            prompt = f"""Create a high-quality digital illustration that represents this crypto gaming market update: 
            {tweet_text}
            Style: {selected_style}, suitable for social media, no text elements"""

            # Generate image using DALL-E
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

            # Download and save image
            image_url = response.data[0].url
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        os.makedirs(self.temp_dir, exist_ok=True)

                        timestamp = int(asyncio.get_event_loop().time())
                        filename = f"image_{timestamp}.png"
                        temp_path = os.path.join(self.temp_dir, filename)

                        with open(temp_path, 'wb') as f:
                            f.write(image_data)

                        logger.info(f"Image saved to {temp_path}")
                        return temp_path

            return None

        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None

    async def cleanup_image(self, image_path: str):
        """Delete temporary image file"""
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)

