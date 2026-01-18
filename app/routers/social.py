from fastapi import APIRouter, Depends, Query
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.services.twitter_service import twitter_service
from app.services.linkedin_service import linkedin_service
from app.services.gmail_service import gmail_service
from app.services.notion_service import notion_service

router = APIRouter()


@router.get("/twitter/test-connection")
async def test_twitter_connection():
    """Test Twitter API connection - Get authenticated user info"""
    return twitter_service.get_my_user_info()


@router.get("/twitter/my-tweets")
async def get_my_tweets(max_results: int = Query(default=10, ge=1, le=100)):
    """Get authenticated user's recent tweets"""
    return twitter_service.get_my_recent_tweets(max_results=max_results)


@router.get("/twitter/user/{username}")
async def search_twitter_user(username: str):
    """Search for a Twitter user by username"""
    return twitter_service.search_user_by_username(username)


@router.post("/twitter/sync-to-memory")
async def sync_twitter_to_memory(
    user_id: int = Query(1, description="User ID"),
    max_tweets: int = Query(50, ge=1, le=100, description="Max tweets to sync")
):
    """Fetch your tweets and save them as memories"""
    from app.services.memory_service import memory_service
    
    # Fetch tweets
    result = twitter_service.get_my_recent_tweets(max_results=max_tweets)
    
    if not result.get("success"):
        return result
    
    tweets = result.get("data", [])
    saved_count = 0
    errors = []
    
    # Save each tweet as a memory
    for tweet in tweets:
        memory_result = memory_service.create_memory(
            user_id=user_id,
            content=tweet["text"],
            source="twitter",
            category="tweet",
            meta_data={
                "likes": tweet.get("likes", 0),
                "retweets": tweet.get("retweets", 0),
                "replies": tweet.get("replies", 0)
            },
            original_post_id=str(tweet["id"]),
            original_url=f"https://twitter.com/i/web/status/{tweet['id']}"
        )
        
        if memory_result.get("success"):
            saved_count += 1
        else:
            errors.append(memory_result.get("error"))
    
    return {
        "success": True,
        "tweets_fetched": len(tweets),
        "memories_saved": saved_count,
        "errors": errors if errors else None,
        "message": f"Successfully synced {saved_count} tweets to memory!"
    }


@router.get("/linkedin/oauth-url")
async def get_linkedin_oauth_url():
    """Get LinkedIn OAuth authorization URL - Step 1"""
    oauth_url = linkedin_service.get_oauth_url()
    return {
        "success": True,
        "oauth_url": oauth_url,
        "instructions": "Visit this URL in your browser to authorize the app. You'll be redirected back with a code."
    }


@router.get("/linkedin/test-token")
async def test_linkedin_token(access_token: str = Query(..., description="LinkedIn access token")):
    """Test LinkedIn API with access token - Get user profile"""
    return linkedin_service.get_user_profile(access_token)


@router.get("/linkedin/my-posts")
async def get_linkedin_posts(
    access_token: str = Query(..., description="LinkedIn access token"),
    count: int = Query(default=10, ge=1, le=50)
):
    """Get user's LinkedIn posts"""
    return linkedin_service.get_user_posts(access_token, count)


@router.post("/linkedin/sync-to-memory")
async def sync_linkedin_to_memory(
    access_token: str = Query(..., description="LinkedIn access token"),
    user_id: int = Query(1, description="User ID")
):
    """Save your LinkedIn profile as a memory"""
    from app.services.memory_service import memory_service
    
    # Fetch profile
    result = linkedin_service.get_user_profile(access_token)
    
    if not result.get("success"):
        return result
    
    profile = result.get("data", {})
    
    # Create structured content
    content = f"""LinkedIn Profile:
Name: {profile.get('name', 'N/A')}
Email: {profile.get('email', 'N/A')}
Profile: {profile.get('sub', 'N/A')}
"""
    
    # Save as memory
    memory_result = memory_service.create_memory(
        user_id=user_id,
        content=content,
        source="linkedin",
        category="profile",
        meta_data=profile,
        original_url="https://www.linkedin.com/in/me"
    )
    
    return {
        "success": memory_result.get("success"),
        "profile_saved": True,
        "memory_id": memory_result.get("memory_id"),
        "message": "LinkedIn profile synced to memory!"
    }


@router.get("/gmail/test-token")
async def test_gmail_token(access_token: str = Query(..., description="Gmail access token")):
    """Test Gmail API with access token - Get user profile"""
    return gmail_service.get_user_profile(access_token)


@router.get("/gmail/my-emails")
async def get_my_emails(
    access_token: str = Query(..., description="Gmail access token"),
    max_results: int = Query(default=10, ge=1, le=50),
    query: str = Query(default="", description="Search query (e.g., 'from:someone@example.com')")
):
    """Get user's recent emails"""
    return gmail_service.get_recent_emails(access_token, max_results, query)


@router.get("/gmail/search")
async def search_gmail(
    access_token: str = Query(..., description="Gmail access token"),
    query: str = Query(..., description="Gmail search query"),
    max_results: int = Query(default=20, ge=1, le=100)
):
    """Search Gmail with specific query"""
    return gmail_service.search_emails(access_token, query, max_results)


@router.get("/notion/test-token")
async def test_notion_token(access_token: str = Query(..., description="Notion access token")):
    """Test Notion API - Search all pages"""
    return notion_service.search_pages(access_token, query="", page_size=10)


@router.get("/notion/search")
async def search_notion_pages(
    access_token: str = Query(..., description="Notion access token"),
    query: str = Query(default="", description="Search query"),
    page_size: int = Query(default=20, ge=1, le=100)
):
    """Search pages in Notion workspace"""
    return notion_service.search_pages(access_token, query, page_size)


@router.get("/notion/page/{page_id}")
async def get_notion_page_content(
    page_id: str,
    access_token: str = Query(..., description="Notion access token")
):
    """Get content from a specific Notion page"""
    return notion_service.get_page_content(access_token, page_id)


@router.post("/notion/sync-to-memory")
async def sync_notion_to_memory(
    access_token: str = Query(..., description="Notion access token"),
    user_id: int = Query(1, description="User ID"),
    max_pages: int = Query(20, ge=1, le=100, description="Max pages to sync")
):
    """Fetch Notion pages and save them as memories"""
    from app.services.memory_service import memory_service
    
    # Search all pages
    search_result = notion_service.search_pages(access_token, query="", page_size=max_pages)
    
    if not search_result.get("success"):
        return search_result
    
    pages = search_result.get("data", [])
    saved_count = 0
    errors = []
    
    # Save each page
    for page in pages:
        page_id = page.get("id")
        
        # Get page content
        content_result = notion_service.get_page_content(access_token, page_id)
        
        if content_result.get("success"):
            page_content = content_result.get("content", "")
            
            # Create structured content
            full_content = f"""Notion Page: {page.get('title', 'Untitled')}

{page_content}

---
Created: {page.get('created_time', 'N/A')}
Last Edited: {page.get('last_edited_time', 'N/A')}
"""
            
            memory_result = memory_service.create_memory(
                user_id=user_id,
                content=full_content,
                source="notion",
                category="document",
                meta_data={
                    "page_id": page_id,
                    "title": page.get("title"),
                    "created_time": page.get("created_time"),
                    "last_edited_time": page.get("last_edited_time")
                },
                original_post_id=page_id,
                original_url=page.get("url"),
                generate_embedding=True
            )
            
            if memory_result.get("success"):
                saved_count += 1
            else:
                errors.append(memory_result.get("error"))
    
    return {
        "success": True,
        "pages_fetched": len(pages),
        "memories_saved": saved_count,
        "errors": errors if errors else None,
        "message": f"Successfully synced {saved_count} Notion pages to memory!"
    }


@router.post("/sync/{platform}")
async def sync_social_platform(
    platform: str,
    current_user: User = Depends(get_current_user)
):
    """Sync memories from social media platform"""
    return {
        "message": f"Syncing {platform} - To be implemented",
        "user_id": current_user.id
    }


@router.get("/accounts")
async def list_connected_accounts(
    current_user: User = Depends(get_current_user)
):
    """List all connected social media accounts"""
    return {
        "message": "List connected accounts - To be implemented",
        "user_id": current_user.id
    }


@router.delete("/accounts/{platform}")
async def disconnect_account(
    platform: str,
    current_user: User = Depends(get_current_user)
):
    """Disconnect a social media account"""
    return {
        "message": f"Disconnect {platform} - To be implemented",
        "user_id": current_user.id
    }
