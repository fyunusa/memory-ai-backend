import re
from typing import Dict, List
from datetime import datetime


class WhatsAppService:
    """Service for parsing WhatsApp chat exports"""
    
    def __init__(self):
        # Pattern for WhatsApp chat export format
        # Matches: [12/31/23, 10:30:45 PM] John Doe: Message text
        # Also matches: 12/31/23, 10:30 PM - John Doe: Message text
        self.message_pattern = re.compile(
            r'[\[]?(\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)[\]]?\s*[-:]?\s*([^:]+):\s*(.+)'
        )
        
        # Alternative pattern for different WhatsApp formats
        self.alt_pattern = re.compile(
            r'(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:AM|PM|am|pm))?)\s*-\s*([^:]+):\s*(.+)'
        )
    
    def parse_whatsapp_chat(self, file_content: str) -> Dict:
        """Parse WhatsApp chat export file"""
        try:
            lines = file_content.split('\n')
            messages = []
            current_message = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Try to match message pattern
                match = self.message_pattern.match(line)
                if not match:
                    match = self.alt_pattern.match(line)
                
                if match:
                    # Save previous message
                    if current_message:
                        messages.append(current_message)
                    
                    # Start new message
                    if len(match.groups()) == 3:
                        timestamp, sender, text = match.groups()
                    else:
                        # Alternative pattern with separate date and time
                        date, time, sender, text = match.groups()
                        timestamp = f"{date}, {time}"
                    
                    current_message = {
                        "timestamp": timestamp,
                        "sender": sender.strip(),
                        "message": text.strip(),
                        "is_system": self._is_system_message(text)
                    }
                else:
                    # Multi-line message continuation
                    if current_message:
                        current_message["message"] += "\n" + line
            
            # Add last message
            if current_message:
                messages.append(current_message)
            
            # Filter out system messages if needed
            user_messages = [msg for msg in messages if not msg["is_system"]]
            
            # Get chat statistics
            stats = self._get_chat_stats(messages)
            
            return {
                "success": True,
                "total_messages": len(messages),
                "user_messages": len(user_messages),
                "system_messages": len(messages) - len(user_messages),
                "data": messages,
                "statistics": stats
            }
        except Exception as e:
            return {"success": False, "error": f"WhatsApp chat parsing failed: {str(e)}"}
    
    def parse_whatsapp_chat_filtered(self, file_content: str, sender_filter: str = None) -> Dict:
        """Parse WhatsApp chat and filter by sender"""
        result = self.parse_whatsapp_chat(file_content)
        
        if not result.get("success"):
            return result
        
        if sender_filter:
            filtered_messages = [
                msg for msg in result["data"]
                if sender_filter.lower() in msg["sender"].lower()
            ]
            
            result["data"] = filtered_messages
            result["filtered_count"] = len(filtered_messages)
            result["filter_applied"] = sender_filter
        
        return result
    
    def _is_system_message(self, text: str) -> bool:
        """Check if message is a system message"""
        system_keywords = [
            "encryption",
            "security code changed",
            "created group",
            "added",
            "left",
            "removed",
            "changed the subject",
            "changed this group's icon",
            "Messages and calls are end-to-end encrypted"
        ]
        
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in system_keywords)
    
    def _get_chat_stats(self, messages: List[Dict]) -> Dict:
        """Get statistics about the chat"""
        if not messages:
            return {}
        
        # Count messages per sender
        sender_counts = {}
        total_words = 0
        
        for msg in messages:
            if msg["is_system"]:
                continue
            
            sender = msg["sender"]
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
            total_words += len(msg["message"].split())
        
        return {
            "participants": list(sender_counts.keys()),
            "participant_count": len(sender_counts),
            "messages_by_sender": sender_counts,
            "total_words": total_words,
            "avg_words_per_message": total_words / len(messages) if messages else 0
        }
    
    def export_to_json(self, messages: List[Dict]) -> str:
        """Export parsed messages to JSON format"""
        import json
        return json.dumps(messages, indent=2)
    
    def search_messages(self, messages: List[Dict], query: str) -> List[Dict]:
        """Search messages by text content"""
        query_lower = query.lower()
        return [
            msg for msg in messages
            if query_lower in msg["message"].lower()
        ]


# Singleton instance
whatsapp_service = WhatsAppService()
