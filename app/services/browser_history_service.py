import json
import csv
from typing import Dict, List
from datetime import datetime
from io import StringIO


class BrowserHistoryService:
    """Service for parsing browser history exports"""
    
    def __init__(self):
        pass
    
    def parse_chrome_history(self, file_content: str) -> Dict:
        """Parse Chrome history export (JSON format)"""
        try:
            data = json.loads(file_content)
            
            if isinstance(data, dict) and "Browser History" in data:
                history = data["Browser History"]
            elif isinstance(data, list):
                history = data
            else:
                history = [data]
            
            parsed_entries = []
            for entry in history:
                parsed_entries.append({
                    "url": entry.get("url", ""),
                    "title": entry.get("title", ""),
                    "visit_count": entry.get("visit_count", 1),
                    "last_visit_time": entry.get("last_visit_time", ""),
                    "typed_count": entry.get("typed_count", 0)
                })
            
            return {
                "success": True,
                "count": len(parsed_entries),
                "data": parsed_entries,
                "source": "Chrome"
            }
        except Exception as e:
            return {"success": False, "error": f"Chrome history parsing failed: {str(e)}"}
    
    def parse_firefox_history(self, file_content: str) -> Dict:
        """Parse Firefox history export (JSON format)"""
        try:
            data = json.loads(file_content)
            
            parsed_entries = []
            for entry in data:
                parsed_entries.append({
                    "url": entry.get("url", ""),
                    "title": entry.get("title", ""),
                    "visit_count": entry.get("visitCount", 1),
                    "last_visit_time": entry.get("lastVisitTime", ""),
                    "typed_count": 0
                })
            
            return {
                "success": True,
                "count": len(parsed_entries),
                "data": parsed_entries,
                "source": "Firefox"
            }
        except Exception as e:
            return {"success": False, "error": f"Firefox history parsing failed: {str(e)}"}
    
    def parse_safari_history(self, file_content: str) -> Dict:
        """Parse Safari history export (CSV format)"""
        try:
            csv_file = StringIO(file_content)
            reader = csv.DictReader(csv_file)
            
            parsed_entries = []
            for row in reader:
                parsed_entries.append({
                    "url": row.get("URL", ""),
                    "title": row.get("Title", ""),
                    "visit_count": int(row.get("Visit Count", 1)),
                    "last_visit_time": row.get("Last Visit", ""),
                    "typed_count": 0
                })
            
            return {
                "success": True,
                "count": len(parsed_entries),
                "data": parsed_entries,
                "source": "Safari"
            }
        except Exception as e:
            return {"success": False, "error": f"Safari history parsing failed: {str(e)}"}
    
    def parse_generic_history(self, file_content: str, format_type: str = "json") -> Dict:
        """Parse browser history in generic format"""
        try:
            if format_type == "json":
                data = json.loads(file_content)
                
                if isinstance(data, list):
                    parsed_entries = []
                    for entry in data:
                        # Handle different possible field names
                        url = entry.get("url") or entry.get("URL") or entry.get("uri")
                        title = entry.get("title") or entry.get("Title") or entry.get("name")
                        
                        parsed_entries.append({
                            "url": url or "",
                            "title": title or "",
                            "visit_count": entry.get("visit_count", entry.get("visitCount", 1)),
                            "last_visit_time": entry.get("last_visit_time", entry.get("lastVisitTime", entry.get("timestamp", ""))),
                            "typed_count": entry.get("typed_count", 0)
                        })
                    
                    return {
                        "success": True,
                        "count": len(parsed_entries),
                        "data": parsed_entries,
                        "source": "Generic JSON"
                    }
            
            elif format_type == "csv":
                csv_file = StringIO(file_content)
                reader = csv.DictReader(csv_file)
                
                parsed_entries = []
                for row in reader:
                    # Handle different possible column names
                    url = row.get("url") or row.get("URL") or row.get("uri")
                    title = row.get("title") or row.get("Title") or row.get("name")
                    
                    parsed_entries.append({
                        "url": url or "",
                        "title": title or "",
                        "visit_count": int(row.get("visit_count", row.get("visitCount", 1))),
                        "last_visit_time": row.get("last_visit_time", row.get("lastVisitTime", row.get("timestamp", ""))),
                        "typed_count": int(row.get("typed_count", 0))
                    })
                
                return {
                    "success": True,
                    "count": len(parsed_entries),
                    "data": parsed_entries,
                    "source": "Generic CSV"
                }
            
            return {"success": False, "error": f"Unsupported format: {format_type}"}
        except Exception as e:
            return {"success": False, "error": f"Generic history parsing failed: {str(e)}"}
    
    def filter_history_by_date(self, entries: List[Dict], start_date: str = None, end_date: str = None) -> List[Dict]:
        """Filter history entries by date range"""
        if not start_date and not end_date:
            return entries
        
        filtered = []
        for entry in entries:
            # This would need proper date parsing based on the format
            # For now, just return all entries
            filtered.append(entry)
        
        return filtered
    
    def group_by_domain(self, entries: List[Dict]) -> Dict:
        """Group history entries by domain"""
        from urllib.parse import urlparse
        
        domains = {}
        for entry in entries:
            try:
                parsed_url = urlparse(entry["url"])
                domain = parsed_url.netloc or parsed_url.path
                
                if domain not in domains:
                    domains[domain] = []
                
                domains[domain].append(entry)
            except:
                continue
        
        return {
            "success": True,
            "domain_count": len(domains),
            "domains": {domain: len(entries) for domain, entries in domains.items()},
            "grouped_data": domains
        }


# Singleton instance
browser_history_service = BrowserHistoryService()
