import json
import os
import requests

def handler(request):
    """Handle both GET (verification) and POST (webhook) requests"""
    
    if request.method == 'GET':
        # Facebook webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        verify_token = os.environ.get('VERIFY_TOKEN', 'my_verify_token')
        
        if mode == 'subscribe' and token == verify_token:
            return challenge
        return 'Forbidden', 403
    
    elif request.method == 'POST':
        # Handle incoming webhook
        try:
            data = request.get_json()
            
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
                                
                                # Don't reply to own comments
                                if sender_id != page_id and 'PROMPT' in message:
                                    reply_to_comment(comment_id)
            
            return json.dumps({"status": "ok"})
        except Exception as e:
            print(f"Error: {e}")
            return json.dumps({"status": "error"})
    
    return 'OK'

def reply_to_comment(comment_id):
    """Reply to a comment with the prompt"""
    token = os.environ.get('FB_ACCESS_TOKEN')
    url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"
    
    message = "🎨 Thanks for your interest!\n\nThe prompt used for this image will be shared soon!\n\n✨ Follow our page for daily AI art!"
    
    payload = {
        "message": message,
        "access_token": token
    }
    
    response = requests.post(url, data=payload)
    print(f"Reply result: {response.json()}")
    return response.json()
