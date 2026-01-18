import requests
from typing import Dict, Optional
from app.config import settings


class LinkedInService:
    def __init__(self):
        """Initialize LinkedIn API client"""
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET
        self.redirect_uri = "http://localhost:8000/oauth/linkedin/callback"
        self.base_url = "https://api.linkedin.com/v2"
        
    def get_oauth_url(self, state: str = "random_state_string") -> str:
        """Generate LinkedIn OAuth authorization URL"""
        scopes = "openid profile email"
        auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&state={state}"
            f"&scope={scopes}"
        )
        return auth_url
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        try:
            token_url = "https://www.linkedin.com/oauth/v2/accessToken"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                return {
                    "success": True,
                    "access_token": token_data.get("access_token"),
                    "expires_in": token_data.get("expires_in")
                }
            
            return {
                "success": False,
                "error": f"Token exchange failed: {response.status_code}",
                "details": response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_profile(self, access_token: str) -> Dict:
        """Get user's LinkedIn profile information using OpenID Connect"""
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "cache-control": "no-cache"
            }
            
            # Use OpenID Connect userinfo endpoint
            profile_url = "https://api.linkedin.com/v2/userinfo"
            profile_response = requests.get(profile_url, headers=headers)
            
            if profile_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Profile fetch failed: {profile_response.status_code}",
                    "details": profile_response.text
                }
            
            profile_data = profile_response.json()
            
            return {
                "success": True,
                "data": {
                    "sub": profile_data.get("sub"),  # User ID
                    "name": profile_data.get("name"),
                    "given_name": profile_data.get("given_name"),
                    "family_name": profile_data.get("family_name"),
                    "email": profile_data.get("email"),
                    "email_verified": profile_data.get("email_verified"),
                    "picture": profile_data.get("picture")
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_posts(self, access_token: str, count: int = 10) -> Dict:
        """Get user's LinkedIn posts"""
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "cache-control": "no-cache",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            # First get user's person URN
            profile_url = f"{self.base_url}/me"
            profile_response = requests.get(profile_url, headers=headers)
            
            if profile_response.status_code != 200:
                return {"success": False, "error": "Could not get user profile"}
            
            user_id = profile_response.json().get("id")
            author_urn = f"urn:li:person:{user_id}"
            
            # Get posts
            posts_url = f"{self.base_url}/ugcPosts"
            params = {
                "q": "authors",
                "authors": author_urn,
                "count": count
            }
            
            posts_response = requests.get(posts_url, headers=headers, params=params)
            
            if posts_response.status_code == 200:
                posts_data = posts_response.json()
                elements = posts_data.get("elements", [])
                
                posts_list = []
                for post in elements:
                    specific_content = post.get("specificContent", {}).get("com.linkedin.ugc.ShareContent", {})
                    share_commentary = specific_content.get("shareCommentary", {})
                    text = share_commentary.get("text", "")
                    
                    posts_list.append({
                        "id": post.get("id"),
                        "text": text,
                        "created_at": post.get("created", {}).get("time"),
                        "visibility": post.get("visibility", {}).get("com.linkedin.ugc.MemberNetworkVisibility")
                    })
                
                return {
                    "success": True,
                    "count": len(posts_list),
                    "data": posts_list
                }
            
            return {
                "success": False,
                "error": f"Posts fetch failed: {posts_response.status_code}",
                "details": posts_response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
linkedin_service = LinkedInService()
