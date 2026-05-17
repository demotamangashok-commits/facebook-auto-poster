from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import parse_qs, urlparse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
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
        
        try:
            if data.get('object') == 'page':
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        if change.get('field') == 'feed':
                            value = change.get('value', {})
                            
                            if value.get('item') == 'comment':
                                comment_id = value.get('comment_id')
                                message = value.get('message', '').upper()
                                sender_id = value.get('sender_id')
                                page_id = os.environ.get('FB_PAGE_ID')
                                
                                if sender_id != page_id and 'PROMPT' in message:
                                    self.reply_to_comment(comment_id)
        except Exception as e:
            print(f"Error: {e}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())
    
    def reply_to_comment(self, comment_id):
        token = os.environ.get('FB_ACCESS_TOKEN')
        url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"
        
        message = "🎨 Thanks for your interest!\n\nFollow our page for daily AI art!"
        
        payload = {"message": message, "access_token": token}
        requests.post(url, data=payload)
