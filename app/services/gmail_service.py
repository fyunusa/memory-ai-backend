from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from typing import Dict, List, Optional
import base64
from email.mime.text import MIMEText
from datetime import datetime
from app.config import settings


class GmailService:
    """Service for integrating with Gmail API"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.metadata'
    ]
    
    def __init__(self):
        self.redirect_uri = getattr(settings, 'GMAIL_REDIRECT_URI', 'http://localhost:8000/oauth/gmail/callback')
    
    def get_oauth_url(self, state: str = "random_state") -> str:
        """Generate Gmail OAuth URL"""
        client_id = getattr(settings, 'GMAIL_CLIENT_ID', 'your-gmail-client-id')
        scopes = ' '.join(self.SCOPES)
        
        return (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&scope={scopes}"
            f"&access_type=offline"
            f"&state={state}"
        )
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        try:
            import requests
            
            client_id = getattr(settings, 'GMAIL_CLIENT_ID', '')
            client_secret = getattr(settings, 'GMAIL_CLIENT_SECRET', '')
            
            data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code"
            }
            
            response = requests.post(
                "https://oauth2.googleapis.com/token",
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return {
                    "success": True,
                    "access_token": token_data.get("access_token"),
                    "refresh_token": token_data.get("refresh_token"),
                    "expires_in": token_data.get("expires_in")
                }
            
            return {
                "success": False,
                "error": f"Token exchange failed: {response.status_code}",
                "details": response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_gmail_service(self, access_token: str):
        """Create Gmail API service instance"""
        credentials = Credentials(token=access_token)
        service = build('gmail', 'v1', credentials=credentials)
        return service
    
    def get_user_profile(self, access_token: str) -> Dict:
        """Get Gmail user profile"""
        try:
            service = self.get_gmail_service(access_token)
            profile = service.users().getProfile(userId='me').execute()
            
            return {
                "success": True,
                "data": {
                    "email": profile.get("emailAddress"),
                    "messages_total": profile.get("messagesTotal"),
                    "threads_total": profile.get("threadsTotal"),
                    "history_id": profile.get("historyId")
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_recent_emails(self, access_token: str, max_results: int = 10, query: str = "") -> Dict:
        """Get recent emails from Gmail"""
        try:
            service = self.get_gmail_service(access_token)
            
            # List messages
            results = service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return {
                    "success": True,
                    "count": 0,
                    "data": [],
                    "message": "No emails found"
                }
            
            emails = []
            for msg in messages:
                # Get full message details
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                email_data = self._parse_email(message)
                emails.append(email_data)
            
            return {
                "success": True,
                "count": len(emails),
                "data": emails
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_emails(self, access_token: str, query: str, max_results: int = 50) -> Dict:
        """Search emails with specific query"""
        return self.get_recent_emails(access_token, max_results, query)
    
    def _parse_email(self, message: Dict) -> Dict:
        """Parse email message data"""
        headers = message.get('payload', {}).get('headers', [])
        
        subject = ""
        sender = ""
        date = ""
        
        for header in headers:
            name = header.get('name', '').lower()
            if name == 'subject':
                subject = header.get('value', '')
            elif name == 'from':
                sender = header.get('value', '')
            elif name == 'date':
                date = header.get('value', '')
        
        # Get email body
        body = self._get_email_body(message.get('payload', {}))
        
        return {
            "id": message.get('id'),
            "thread_id": message.get('threadId'),
            "subject": subject,
            "from": sender,
            "date": date,
            "snippet": message.get('snippet', ''),
            "body": body,
            "labels": message.get('labelIds', [])
        }
    
    def _get_email_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        if 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    if 'data' in part.get('body', {}):
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
        
        return ""


# Singleton instance
gmail_service = GmailService()
