from fastapi import APIRouter, Query
from app.services.linkedin_service import linkedin_service
from app.services.gmail_service import gmail_service
from app.services.notion_service import notion_service

router = APIRouter()


@router.get("/facebook")
async def facebook_oauth_init():
    """Initiate Facebook OAuth flow"""
    return {"message": "Facebook OAuth - To be implemented"}


@router.get("/facebook/callback")
async def facebook_oauth_callback():
    """Facebook OAuth callback handler"""
    return {"message": "Facebook OAuth callback - To be implemented"}


@router.get("/twitter")
async def twitter_oauth_init():
    """Initiate Twitter OAuth flow"""
    return {"message": "Twitter OAuth - To be implemented"}


@router.get("/twitter/callback")
async def twitter_oauth_callback():
    """Twitter OAuth callback handler"""
    return {"message": "Twitter OAuth callback - To be implemented"}


@router.get("/linkedin")
async def linkedin_oauth_init():
    """Initiate LinkedIn OAuth flow - Get authorization URL"""
    oauth_url = linkedin_service.get_oauth_url()
    return {
        "success": True,
        "oauth_url": oauth_url,
        "instructions": "Visit this URL to authorize. You'll be redirected to /oauth/linkedin/callback with a code."
    }


@router.get("/linkedin/callback")
async def linkedin_oauth_callback(
    code: str = Query(default=None, description="Authorization code from LinkedIn"),
    state: str = Query(default=None, description="State parameter for CSRF protection"),
    error: str = Query(default=None, description="Error code if authorization failed"),
    error_description: str = Query(default=None, description="Error description")
):
    """LinkedIn OAuth callback - Exchange code for access token"""
    
    # Check if there was an error
    if error:
        return {
            "success": False,
            "error": error,
            "error_description": error_description,
            "message": "LinkedIn authorization failed. Check if your app has the required products approved."
        }
    
    # Check if code is present
    if not code:
        return {
            "success": False,
            "error": "no_code",
            "message": "No authorization code received from LinkedIn. Your app may need verification."
        }
    
    result = linkedin_service.exchange_code_for_token(code)
    
    if result.get("success"):
        return {
            "success": True,
            "access_token": result["access_token"],
            "expires_in": result["expires_in"],
            "message": "Save this access_token to test LinkedIn endpoints!"
        }
    
    return result


@router.get("/gmail")
async def gmail_oauth_init():
    """Initiate Gmail OAuth flow - Get authorization URL"""
    oauth_url = gmail_service.get_oauth_url()
    return {
        "success": True,
        "oauth_url": oauth_url,
        "instructions": "Visit this URL to authorize Gmail access. You'll be redirected to /oauth/gmail/callback with a code."
    }


@router.get("/gmail/callback")
async def gmail_oauth_callback(
    code: str = Query(default=None, description="Authorization code from Google"),
    state: str = Query(default=None, description="State parameter for CSRF protection"),
    error: str = Query(default=None, description="Error code if authorization failed")
):
    """Gmail OAuth callback - Exchange code for access token"""
    
    if error:
        return {
            "success": False,
            "error": error,
            "message": "Gmail authorization failed."
        }
    
    if not code:
        return {
            "success": False,
            "error": "no_code",
            "message": "No authorization code received from Google."
        }
    
    result = gmail_service.exchange_code_for_token(code)
    
    if result.get("success"):
        return {
            "success": True,
            "access_token": result["access_token"],
            "refresh_token": result.get("refresh_token"),
            "expires_in": result["expires_in"],
            "message": "Save this access_token to test Gmail endpoints!"
        }
    
    return result


@router.get("/notion")
async def notion_oauth_init():
    """Initiate Notion OAuth flow - Get authorization URL"""
    oauth_url = notion_service.get_oauth_url()
    return {
        "success": True,
        "oauth_url": oauth_url,
        "instructions": "Visit this URL to authorize Notion access. You'll be redirected to /oauth/notion/callback with a code."
    }


@router.get("/notion/callback")
async def notion_oauth_callback(
    code: str = Query(default=None, description="Authorization code from Notion"),
    state: str = Query(default=None, description="State parameter for CSRF protection"),
    error: str = Query(default=None, description="Error code if authorization failed")
):
    """Notion OAuth callback - Exchange code for access token"""
    
    if error:
        return {
            "success": False,
            "error": error,
            "message": "Notion authorization failed."
        }
    
    if not code:
        return {
            "success": False,
            "error": "no_code",
            "message": "No authorization code received from Notion."
        }
    
    result = notion_service.exchange_code_for_token(code)
    
    if result.get("success"):
        return {
            "success": True,
            "access_token": result["access_token"],
            "workspace_id": result.get("workspace_id"),
            "workspace_name": result.get("workspace_name"),
            "message": "Save this access_token to test Notion endpoints!"
        }
    
    return result

