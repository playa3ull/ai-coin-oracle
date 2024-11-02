import tweepy
import logging
import pytz
import os
from dotenv import load_dotenv
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommentReplyService:
    def __init__(self, llm_service):
        load_dotenv()
        self.llm = llm_service

        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            wait_on_rate_limit=True
        )

        # Track conversation counts for monitoring
        self.conversation_counts = {}
        self.MAX_REPLIES = 3  # Alert if conversation exceeds this number

    async def check_and_reply_to_comments(self):
        """Monitor and reply to comments using v2 endpoints"""
        try:
            me = self.client.get_me()
            bot_id = me.data.id
            logger.info(f"Checking replies for bot ID: {bot_id}")

            # Get recent tweets by the bot
            tweets = self.client.get_users_tweets(
                id=bot_id,
                max_results=10,
                tweet_fields=['conversation_id', 'created_at']
            )

            if not tweets.data:
                logger.info("No tweets found to check for replies")
                return

            # Check each tweet for replies
            for tweet in tweets.data:
                await self.check_tweet_replies(tweet.id, bot_id)

        except Exception as e:
            logger.error(f"Error in reply monitoring: {str(e)}")

    async def check_tweet_replies(self, tweet_id, bot_id):
        """Check and handle replies to a specific tweet"""
        try:
            # Search for replies to this tweet
            query = f"conversation_id:{tweet_id} -from:{bot_id}"
            replies = self.client.search_recent_tweets(
                query=query,
                max_results=10,
                tweet_fields=['conversation_id', 'created_at', 'in_reply_to_user_id'],
                expansions=['author_id']
            )

            if not replies.data:
                return

            logger.info(f"Found {len(replies.data)} replies to tweet {tweet_id}")

            # Process each reply
            # for reply in replies.data:
            #     await self.handle_reply(reply, tweet_id)

        except Exception as e:
            logger.error(f"Error checking replies for tweet {tweet_id}: {str(e)}")

    async def handle_reply(self, reply, original_tweet_id):
        """Generate and post a reply, with monitoring"""
        try:
            # Check conversation count
            conversation_id = reply.conversation_id
            self.conversation_counts[conversation_id] = self.conversation_counts.get(conversation_id, 0) + 1

            # Alert if conversation is getting long
            if self.conversation_counts[conversation_id] >= self.MAX_REPLIES:
                self.alert_team(conversation_id)
                return

            # Get original tweet text for context
            original_tweet = self.client.get_tweet(
                original_tweet_id,
                tweet_fields=['text']
            )

            # Generate reply using GPT-4
            prompt = f"""
            You are a friendly crypto gaming expert. Generate a brief reply to this comment.
            Original Tweet: {original_tweet.data.text}
            Comment: {reply.text}
            Requirements: 
            - Keep under 240 chars
            - Be friendly and informative
            - No price predictions
            - Use relevant emojis
            - Focus only on gaming and crypto topics
            - Avoid controversial or inflammatory responses
            """

            response = await self.llm.acomplete(prompt)
            reply_text = response.text.strip()

            # Post the reply
            response = self.client.create_tweet(
                text=reply_text,
                in_reply_to_tweet_id=reply.id
            )

            logger.info(f"Posted reply to tweet {reply.id}")

        except Exception as e:
            logger.error(f"Error handling reply: {str(e)}")

    def alert_team(self, conversation_id):
        """Alert the team about a long conversation"""
        logger.warning(f"⚠️ Alert: Conversation {conversation_id} has reached {self.MAX_REPLIES} replies.")
        # Here you could add additional notification methods:
        # - Send email
        # - Post to Slack/Discord
        # - Send SMS
        # etc.


# Test code
if __name__ == "__main__":
    from src.services.llm import LLMService


    async def test_service():
        llm_service = LLMService()
        service = CommentReplyService(llm_service)

        print("\n=== Testing Comment Reply Service ===")

        try:
            # Test authentication
            me = service.client.get_me()
            print(f"✓ Authenticated as @{me.data.username}")

            # Test reply monitoring
            print("\nChecking for replies...")
            await service.check_and_reply_to_comments()
            print("✓ Reply check completed")

        except Exception as e:
            print(f"Error during test: {str(e)}")


    asyncio.run(test_service())