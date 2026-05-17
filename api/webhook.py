import os
import requests
import logging
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Environment variables
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")
GRAPH_API_VERSION = "v19.0"

# Store Page ID
PAGE_ID = None

# Your prompt message
PHOTO_PROMPT = """🎨 Here's the prompt!

✨ "A mystical forest with bioluminescent trees, ethereal fog, cinematic lighting, 8k, ultra detailed"

🔧 Model: Midjourney v6
📐 Aspect: 16:9

🌟 Follow for more prompts!"""


def get_page_id():
    try:
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/me"
        params = {"access_token": PAGE_ACCESS_TOKEN}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("id")
    except Exception as e:
        logger.error(f"Error getting page ID: {e}")
    return None


def reply_to_comment(comment_id, message):
    try:
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{comment_id}/comments"
        payload = {
            "message": message,
            "access_token": PAGE_ACCESS_TOKEN
        }
        response = requests.post(url, data=payload)
        result = response.json()
        
        if "id" in result:
            logger.info(f"Reply posted: {result}")
            return True
        else:
            logger.error(f"Reply failed: {result}")
            return False
    except Exception as e:
        logger.error(f"Error replying: {e}")
        return False


@app.get("/api/webhook")
def verify(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook verified!")
        return PlainTextResponse(content=challenge)
    
    return PlainTextResponse(content="Forbidden", status_code=403)


@app.post("/api/webhook")
async def webhook(request: Request):
    global PAGE_ID
    
    if PAGE_ID is None:
        PAGE_ID = get_page_id()
    
    try:
        data = await request.json()
        logger.info(f"Received: {data}")
    except Exception as e:
        logger.error(f"JSON error: {e}")
        return PlainTextResponse(content="Error", status_code=400)

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                item = value.get("item")
                verb = value.get("verb")
                
                if item == "comment" and verb == "add":
                    sender_id = value.get("from", {}).get("id")
                    sender_name = value.get("from", {}).get("name", "Friend")
                    comment_id = value.get("comment_id")
                    message = value.get("message", "").lower()
                    
                    logger.info(f"Comment from {sender_name}: {message}")
                    
                    # Skip own comments
                    if sender_id == PAGE_ID:
                        logger.info("Skipping own comment")
                        continue
                    
                    # Check trigger words
                    triggers = ["prompt", "how", "what", "please", "share", "send"]
                    should_reply = any(word in message for word in triggers)
                    
                    if should_reply and comment_id:
                        reply = f"Hi {sender_name}! 👋\n\n{PHOTO_PROMPT}"
                        reply_to_comment(comment_id, reply)
                        
    except Exception as e:
        logger.error(f"Processing error: {e}")

    return PlainTextResponse(content="EVENT_RECEIVED", status_code=200)


@app.get("/")
def root():
    return {"status": "Bot is running!"}
