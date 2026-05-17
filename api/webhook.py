from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

def reply_to_comment(comment_id, message):
    token = os.environ.get('FB_ACCESS_TOKEN')
    url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"
    payload = {"message": message, "access_token": token}
    response = requests.post(url, data=payload)
    return response.json()

@app.route('/api/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    verify_token = os.environ.get('VERIFY_TOKEN', 'my_verify_token')
    
    if mode == 'subscribe' and token == verify_token:
        return challenge, 200
    return 'Forbidden', 403

@app.route('/api/webhook', methods=['POST'])
def webhook():
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
                        
                        if sender_id != page_id and 'PROMPT' in message:
                            reply = "🎨 Thanks for your interest! The prompt will be shared soon. Follow for more AI art!"
                            reply_to_comment(comment_id, reply)
    
    return jsonify({"status": "ok"}), 200

@app.route('/')
def home():
    return 'Facebook Auto-Poster Webhook is running!'

if __name__ == '__main__':
    app.run()
