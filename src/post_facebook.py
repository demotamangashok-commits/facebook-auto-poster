import os
import requests

def post_to_facebook(image_url, caption):
    page_id = os.environ.get("FB_PAGE_ID")
    access_token = os.environ.get("FB_ACCESS_TOKEN")
    
    url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
    
    payload = {
        "url": image_url,
        "message": caption,
        "access_token": access_token
    }
    
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Facebook post failed: {response.text}")

if __name__ == "__main__":
    print("Facebook module ready")
