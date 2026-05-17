from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import parse_qs

# Store prompts (in production, use a database)
PROMPTS = {}

def get_page_access_token():
    return os.environ.get('FB_ACCESS_TOKEN')

def get_page_id():
    return os.environ.get('FB_PAGE_ID')

def reply_to_comment(comment_id, message):
    """Reply to a comment"""
    token = get_page_access_token()
    url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"
    
    payload = {
        "message": message,
        "access_token": token
    }
    
    response = requests.post(url, data=payload)
    return response.json()

def get_post_prompt(post_id):
    """Get the prompt for a post"""
    # For now, return a default message
    # Later we can store prompts in a database
    return PROMPTS.get(post_id, "Thank you for your interest! The prompt for this image will be shared soon. Follow our page for more AI art!")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle webhook verification"""
        try:
            # Parse query parameters
            query = parse_qs(self.path.split('?')[1]) if '?' in self.path else {}
            
            mode = query.get('hub.mode', [None])[0]
            token = query.get('hub.verify_token', [None])[0]
            challenge = query.get('hub.challenge', [None])[0]
            
            verify_token = os.environ.get('VERIFY_TOKEN', 'my_verify_token')
            
            if mode == 'subscribe' and token == verify_token:
                print("Webhook verified!")
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(challenge.encode())
            else:
                self.send_response(403)
                self.end_headers()
        except Exception as e:
            print(f"Verification error: {e}")
            self.send_response(400)
            self.end_headers()
    
    def do_POST(self):
        """Handle incoming webhooks from Facebook"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"Received webhook: {json.dumps(data, indent=2)}")
            
            # Process the webhook
            if data.get('object') == 'page':
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        if change.get('field') == 'feed':
                            value = change.get('value', {})
                            
                            # Check if it's a comment
                            if value.get('item') == 'comment':
                                comment_id = value.get('comment_id')
                                message = value.get('message', '').upper()
                                post_id = value.get('post_id')
                                sender_id = value.get('sender_id')
                                page_id = get_page_id()
                                
                                # Don't reply to our own comments
                                if sender_id == page_id:
                                    print("Skipping own comment")
                                    continue
                                
                                # Check if comment contains "PROMPT"
                                if 'PROMPT' in message:
                                    print(f"Prompt request from comment: {comment_id}")
                                    prompt = get_post_prompt(post_id)
                                    reply_message = f"🎨 Here's the prompt used:\n\n{prompt}\n\n✨ Follow for daily AI art!"
                                    result = reply_to_comment(comment_id, reply_message)
                                    print(f"Reply result: {result}")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            
        except Exception as e:
            print(f"Webhook error: {e}")
            self.send_response(200)  # Always return 200 to Facebook
            self.end_headers()
