from fastapi import APIRouter, UploadFile, File, Form, Query
from typing import Optional
from app.services.file_service import file_service
from app.services.browser_history_service import browser_history_service
from app.services.whatsapp_service import whatsapp_service

router = APIRouter()


@router.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(default="document"),
    description: Optional[str] = Form(default=None)
):
    """Upload document file (txt, pdf, docx) and extract text"""
    try:
        # Read file content
        content = await file.read()
        
        # Process file
        result = file_service.process_file(file.filename, content)
        
        if not result.get("success"):
            return result
        
        # Add metadata
        result["category"] = category
        result["description"] = description
        result["upload_status"] = "processed"
        
        # Chunk text for embeddings
        chunks = file_service.chunk_text(result["text"])
        result["chunk_count"] = len(chunks)
        result["chunks"] = chunks[:3]  # Return first 3 chunks as preview
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/upload/browser-history")
async def upload_browser_history(
    file: UploadFile = File(...),
    browser_type: str = Form(default="chrome"),
    format_type: str = Form(default="json")
):
    """Upload browser history export file"""
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        if browser_type == "chrome":
            result = browser_history_service.parse_chrome_history(content_str)
        elif browser_type == "firefox":
            result = browser_history_service.parse_firefox_history(content_str)
        elif browser_type == "safari":
            result = browser_history_service.parse_safari_history(content_str)
        else:
            result = browser_history_service.parse_generic_history(content_str, format_type)
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/upload/whatsapp-chat")
async def upload_whatsapp_chat(
    file: UploadFile = File(...),
    sender_filter: Optional[str] = Form(default=None)
):
    """Upload WhatsApp chat export file"""
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        if sender_filter:
            result = whatsapp_service.parse_whatsapp_chat_filtered(content_str, sender_filter)
        else:
            result = whatsapp_service.parse_whatsapp_chat(content_str)
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/upload/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "success": True,
        "formats": {
            "documents": {
                "types": [".txt", ".pdf", ".docx"],
                "max_size": "10MB",
                "endpoint": "/upload/document"
            },
            "browser_history": {
                "types": [".json", ".csv"],
                "browsers": ["chrome", "firefox", "safari", "generic"],
                "endpoint": "/upload/browser-history"
            },
            "whatsapp": {
                "types": [".txt"],
                "format": "WhatsApp chat export",
                "endpoint": "/upload/whatsapp-chat"
            }
        }
    }
