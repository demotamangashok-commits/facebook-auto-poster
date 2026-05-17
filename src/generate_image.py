import os
import requests
import time

def generate_image(prompt):
    # Using a free model that works
    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    headers = {"Authorization": f"Bearer {os.environ.get('HF_TOKEN')}"}
    
    payload = {
        "inputs": prompt,
    }
    
    # Try up to 3 times (model may need to wake up)
    for attempt in range(3):
        print(f"Attempt {attempt + 1}...")
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            with open("generated_image.png", "wb") as f:
                f.write(response.content)
            return "generated_image.png"
        elif response.status_code == 503:
            # Model is loading, wait and retry
            print("Model is loading, waiting 30 seconds...")
            time.sleep(30)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    raise Exception(f"Image generation failed after 3 attempts")

if __name__ == "__main__":
    generate_image("A beautiful sunset over mountains")
