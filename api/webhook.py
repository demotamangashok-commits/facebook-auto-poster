from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import parse_qs, urlparse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        mode = params.get('hub.mode', [None])[0]
        token = params.get('hub.verify_token', [None])[0]
        challenge = params.get('hub.challenge', [None])[0]
        
        verify_token = os.environ.get('VERIFY_TOKEN', 'my_verify_token')
        
        if mode == 'subscribe' and token == verify_token:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(challenge.encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Webhook is running!')
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        # Log received data
        print(f"=== WEBHOOK RECEIVED ===")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        try:
            if data.get('object') == 'page':
                for entry in data.get('entry', []):
                    # Check for changes (new format)
                    for change in entry.get('changes', []):
                        print(f"Change: {change}")
                        if change.get('field') == 'feed':
                            value = change.get('value', {})
                            item = value.get('item')
                            verb = value.get('verb')
                            
                            print(f"Item: {item}, Verb: {verb}")
                            
                            if item == 'comment' and verb == 'add':
                                comment_id = value.get('comment_id')
                                message = value.get('message', '')
                                sender_id = value.get('sender_id')
                                sender_name = value.get('sender_name', 'Unknown')
                                
                                print(f"Comment from {sender_name}: {message}")
                                print(f"Comment ID: {comment_id}")
                                
                                page_id = os.environ.get('FB_PAGE_ID')
                                
                                if sender_id != page_id and 'PROMPT' in message.upper():
                                    print(f">>> PROMPT detected! Replying...")
                                    result = self.reply_to_comment(comment_id)
                                    print(f"Reply result: {result}")
                                else:
                                    print(f"No PROMPT in message or own comment")
        except Exception as e:
            print(f"Error processing webhook: {e}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())
    
    def reply_to_comment(self, comment_id):
        token = os.environ.get('FB_ACCESS_TOKEN')
        url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"
        
        message = "🎨 Thanks for your interest!\n\nThe prompt used for this image will be shared soon!\n\n✨ Follow our page for daily AI art!"
        
        payload = {"message": message, "access_token": token}
        
        print(f"Sending reply to: {url}")
        response = requests.post(url, data=payload)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        return response.json()
