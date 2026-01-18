import tweepy
from app.config import settings
from typing import List, Dict, Optional


class TwitterService:
    def __init__(self):
        """Initialize Twitter API client with OAuth 1.0a credentials"""
        self.client = tweepy.Client(
            bearer_token=settings.TWITTER_BEARER_TOKEN,
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
        )
    
    def get_my_user_info(self) -> Dict:
        """Get authenticated user's information"""
        try:
            me = self.client.get_me(
                user_fields=['id', 'name', 'username', 'description', 'created_at', 'public_metrics']
            )
            
            if me.data:
                return {
                    "success": True,
                    "data": {
                        "id": me.data.id,
                        "name": me.data.name,
                        "username": me.data.username,
                        "description": me.data.description,
                        "created_at": str(me.data.created_at),
                        "followers_count": me.data.public_metrics.get('followers_count'),
                        "following_count": me.data.public_metrics.get('following_count'),
                        "tweet_count": me.data.public_metrics.get('tweet_count')
                    }
                }
            return {"success": False, "error": "No data returned"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_my_recent_tweets(self, max_results: int = 10) -> Dict:
        """Get authenticated user's recent tweets"""
        try:
            # First get user ID
            me = self.client.get_me()
            if not me.data:
                return {"success": False, "error": "Could not get user ID"}
            
            user_id = me.data.id
            
            # Get user's tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['id', 'text', 'created_at', 'public_metrics']
            )
            
            if tweets.data:
                tweet_list = []
                for tweet in tweets.data:
                    tweet_list.append({
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": str(tweet.created_at),
                        "likes": tweet.public_metrics.get('like_count', 0),
                        "retweets": tweet.public_metrics.get('retweet_count', 0),
                        "replies": tweet.public_metrics.get('reply_count', 0)
                    })
                
                return {
                    "success": True,
                    "count": len(tweet_list),
                    "data": tweet_list
                }
            
            return {"success": True, "count": 0, "data": [], "message": "No tweets found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_user_by_username(self, username: str) -> Dict:
        """Search for a user by username"""
        try:
            user = self.client.get_user(
                username=username,
                user_fields=['id', 'name', 'username', 'description', 'public_metrics']
            )
            
            if user.data:
                return {
                    "success": True,
                    "data": {
                        "id": user.data.id,
                        "name": user.data.name,
                        "username": user.data.username,
                        "description": user.data.description,
                        "followers_count": user.data.public_metrics.get('followers_count'),
                        "following_count": user.data.public_metrics.get('following_count')
                    }
                }
            return {"success": False, "error": "User not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
twitter_service = TwitterService()
