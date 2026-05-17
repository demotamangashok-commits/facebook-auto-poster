import os
import requests
import time

def generate_image(prompt):
    # Using FLUX model - free and working
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {os.environ.get('HF_TOKEN')}"}
    
    payload = {
        "inputs": prompt,
    }
    
    # Try up to 5 times (model may need to wake up)
    for attempt in range(5):
        print(f"Attempt {attempt + 1}...")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            with open("generated_image.png", "wb") as f:
                f.write(response.content)
            print("Image generated successfully!")
            return "generated_image.png"
        elif response.status_code == 503:
            # Model is loading, wait and retry
            wait_time = 60
            print(f"Model is loading, waiting {wait_time} seconds...")
            time.sleep(wait_time)
        elif response.status_code == 500:
            print("Server error, retrying in 30 seconds...")
            time.sleep(30)
        else:
            print(f"Error: {response.status_code}")
            print(response.text[:500])
            time.sleep(10)
    
    raise Exception("Image generation failed after 5 attempts")

if __name__ == "__main__":
    generate_image("A beautiful sunset over mountains")
