import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Environment variables
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
GRAPH_API_VERSION = "v19.0"

# Cache Page ID
PAGE_ID = None

# ============================================
# YOUR PHOTO PROMPT - CUSTOMIZE THIS!
# ============================================
PHOTO_PROMPT = """🎨 Here's the prompt you requested!

✨ Prompt: "A mystical forest with bioluminescent trees, ethereal fog, cinematic lighting, 8k, ultra detailed, fantasy art"

🔧 Settings:
• Model: Midjourney v6
• Aspect: 16:9
• Stylize: 750

🌟 Follow our page for daily AI prompts!"""


def get_page_id():
    """Get Page ID"""
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/me"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("id")
    except:
        pass
    return None


def reply_to_comment(comment_id: str, message: str):
    """Reply to a comment - FREE, no special permissions!"""
    
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{comment_id}/comments"
    
    payload = {
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, data=payload)
        result = response.json()
        
        if "id" in result:
            logger.info(f"✅ Reply posted successfully!")
            return True, result
        else:
            logger.error(f"❌ Reply failed: {result}")
            return False, result
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False, str(e)


@app.get("/api/webhook")
async def verify(request: Request):
    """Webhook verification"""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("✅ Webhook verified!")
        return PlainTextResponse(content=challenge)
    
    return PlainTextResponse(content="Forbidden", status_code=403)


@app.post("/api/webhook")
async def webhook(request: Request):
    """Handle webhook events"""
    global PAGE_ID
    
    if PAGE_ID is None:
        PAGE_ID = get_page_id()
        logger.info(f"Page ID: {PAGE_ID}")
    
    try:
        data = await request.json()
        logger.info(f"📥 Received: {data}")
    except:
        return PlainTextResponse(content="Error", status_code=400)

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                item = value.get("item")
                verb = value.get("verb")
                
                logger.info(f"Item: {item}, Verb: {verb}")
                
                # New comment added
                if item == "comment" and verb == "add":
                    
                    sender_id = value.get("from", {}).get("id")
                    sender_name = value.get("from", {}).get("name", "Friend")
                    comment_id = value.get("comment_id")
                    message = value.get("message", "").lower()
                    
                    logger.info(f"💬 Comment from {sender_name}: {message}")
                    
                    # Skip own comments
                    if sender_id == PAGE_ID:
                        logger.info("⏭️ Skipping own comment")
                        continue
                    
                    # Check if user wants the prompt
                    # Reply to ALL comments OR only specific keywords
                    trigger_words = ["prompt", "how", "what", "please", "share", "send", "dm", "inbox"]
                    
                    should_reply = any(word in message for word in trigger_words)
                    
                    # Option: Reply to ALL comments (uncomment below)
                    # should_reply = True
                    
                    if should_reply and comment_id:
                        reply_message = f"Hi @{sender_name}! 👋\n\n{PHOTO_PROMPT}"
                        
                        success, result = reply_to_comment(comment_id, reply_message)
                        
                        if success:
                            logger.info(f"✅ Replied to {sender_name}")
                        else:
                            logger.error(f"❌ Failed: {result}")
                    else:
                        logger.info("⏭️ No trigger word found, skipping")
                        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

    return PlainTextResponse(content="EVENT_RECEIVED", status_code=200)


@app.get("/")
async def root():
    return {"status": "🤖 Bot is running!", "cost": "FREE!"}
