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
        
        print(f"=== WEBHOOK RECEIVED ===")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        try:
            if data.get('object') == 'page':
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        print(f"Change: {change}")
                        if change.get('field') == 'feed':
                            value = change.get('value', {})
                            item = value.get('item')
                            verb = value.get('verb')
                            
                            print(f"Item: {item}, Verb: {verb}")
                            
                            if item == 'comment' and verb == 'add':
                                # Try different ways to get comment ID
                                comment_id = value.get('comment_id')
                                
                                # If comment_id contains underscore, extract the real ID
                                if comment_id and '_' in comment_id:
                                    # Format: postid_commentid - we need the full thing for replies
                                    pass
                                
                                message = value.get('message', '')
                                sender_id = value.get('sender_id') or value.get('from', {}).get('id')
                                sender_name = value.get('sender_name') or value.get('from', {}).get('name', 'Unknown')
                                post_id = value.get('post_id')
                                
                                print(f"Comment from {sender_name}: {message}")
                                print(f"Comment ID: {comment_id}")
                                print(f"Post ID: {post_id}")
                                print(f"Sender ID: {sender_id}")
                                
                                page_id = os.environ.get('FB_PAGE_ID')
                                
                                if sender_id != page_id and 'PROMPT' in message.upper():
                                    print(f">>> PROMPT detected! Replying...")
                                    result = self.reply_to_comment(comment_id, post_id)
                                    print(f"Reply result: {result}")
                                else:
                                    print(f"No PROMPT in message or own comment")
        except Exception as e:
            print(f"Error processing webhook: {e}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())
    
    def reply_to_comment(self, comment_id, post_id):
        token = os.environ.get('FB_ACCESS_TOKEN')
        
        # Try replying to the comment directly
        url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"
        
        message = "🎨 Thanks for your interest!\n\nThe prompt used for this image will be shared soon!\n\n✨ Follow our page for daily AI art!"
        
        payload = {"message": message, "access_token": token}
        
        print(f"Sending reply to: {url}")
        response = requests.post(url, data=payload)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        # If that fails, try commenting on the post instead
        if response.status_code != 200:
            print("Direct reply failed, trying to comment on post...")
            url = f"https://graph.facebook.com/v19.0/{post_id}/comments"
            print(f"Commenting on post: {url}")
            response = requests.post(url, data=payload)
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        
        return response.json()
