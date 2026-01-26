import requests
from typing import Dict, List, Optional
from datetime import datetime
from app.config import settings


class NotionService:
    """Service for integrating with Notion API"""
    
    def __init__(self):
        self.base_url = "https://api.notion.com/v1"
        self.version = "2022-06-28"
    
    def get_headers(self, access_token: str) -> Dict:
        """Get headers for Notion API requests"""
        return {
            "Authorization": f"Bearer {access_token}",
            "Notion-Version": self.version,
            "Content-Type": "application/json"
        }
    
    def get_oauth_url(self, state: str = "random_state") -> str:
        """Generate Notion OAuth URL"""
        client_id = getattr(settings, 'NOTION_CLIENT_ID', 'your-notion-client-id')
        redirect_uri = getattr(settings, 'NOTION_REDIRECT_URI', 'https://memory-ai-backend.onrender.com/oauth/notion/callback')
        print(f"[Notion OAuth] get_oauth_url using redirect_uri: {redirect_uri}")
        return (
            f"https://api.notion.com/v1/oauth/authorize"
            f"?client_id={client_id}"
            f"&response_type=code"
            f"&owner=user"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
        )
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        try:
            client_id = getattr(settings, 'NOTION_CLIENT_ID', '')
            client_secret = getattr(settings, 'NOTION_CLIENT_SECRET', '')
            redirect_uri = getattr(settings, 'NOTION_REDIRECT_URI', 'https://memory-ai-backend.onrender.com/oauth/notion/callback')
            print(f"[Notion OAuth] exchange_code_for_token using redirect_uri: {redirect_uri}")
            auth_string = f"{client_id}:{client_secret}"
            import base64
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            headers = {
                "Authorization": f"Basic {encoded_auth}",
                "Content-Type": "application/json"
            }
            data = {
                "grant_type": "authorization_code",
                "code": code
                # 'redirect_uri' omitted as workaround
            }
            response = requests.post(
                "https://api.notion.com/v1/oauth/token",
                headers=headers,
                json=data
            )
            if response.status_code == 200:
                token_data = response.json()
                return {
                    "success": True,
                    "access_token": token_data.get("access_token"),
                    "workspace_id": token_data.get("workspace_id"),
                    "workspace_name": token_data.get("workspace_name")
                }
            return {
                "success": False,
                "error": f"Token exchange failed: {response.status_code}",
                "details": response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_pages(self, access_token: str, query: str = "", page_size: int = 100) -> Dict:
        """Search for pages in Notion workspace"""
        try:
            headers = self.get_headers(access_token)
            
            data = {
                "page_size": page_size
            }
            
            if query:
                data["query"] = query
            
            response = requests.post(
                f"{self.base_url}/search",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                results = response.json()
                pages = []
                
                for result in results.get("results", []):
                    if result.get("object") == "page":
                        pages.append({
                            "id": result.get("id"),
                            "title": self._extract_title(result),
                            "created_time": result.get("created_time"),
                            "last_edited_time": result.get("last_edited_time"),
                            "url": result.get("url")
                        })
                
                return {
                    "success": True,
                    "count": len(pages),
                    "data": pages
                }
            
            return {
                "success": False,
                "error": f"Search failed: {response.status_code}",
                "details": response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_page_content(self, access_token: str, page_id: str) -> Dict:
        """Get content blocks from a Notion page"""
        try:
            headers = self.get_headers(access_token)
            
            response = requests.get(
                f"{self.base_url}/blocks/{page_id}/children",
                headers=headers
            )
            
            if response.status_code == 200:
                blocks = response.json().get("results", [])
                content_parts = []
                
                for block in blocks:
                    text = self._extract_text_from_block(block)
                    if text:
                        content_parts.append(text)
                
                full_content = "\n".join(content_parts)
                
                return {
                    "success": True,
                    "page_id": page_id,
                    "content": full_content,
                    "block_count": len(blocks),
                    "word_count": len(full_content.split())
                }
            
            return {
                "success": False,
                "error": f"Failed to fetch page: {response.status_code}",
                "details": response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_title(self, page: Dict) -> str:
        """Extract title from page object"""
        properties = page.get("properties", {})
        
        for prop_name, prop_value in properties.items():
            if prop_value.get("type") == "title":
                title_array = prop_value.get("title", [])
                if title_array:
                    return title_array[0].get("plain_text", "Untitled")
        
        return "Untitled"
    
    def _extract_text_from_block(self, block: Dict) -> str:
        """Extract text content from a Notion block"""
        block_type = block.get("type")
        
        if not block_type:
            return ""
        
        block_content = block.get(block_type, {})
        
        # Handle different block types
        if "rich_text" in block_content:
            text_array = block_content["rich_text"]
            return " ".join([item.get("plain_text", "") for item in text_array])
        
        return ""


# Singleton instance
notion_service = NotionService()
