import os
import requests

def generate_image(prompt):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.environ.get('HF_TOKEN')}"}
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": "blurry, bad quality, distorted, ugly, deformed"
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        with open("generated_image.png", "wb") as f:
            f.write(response.content)
        return "generated_image.png"
    else:
        raise Exception(f"Image generation failed: {response.text}")

if __name__ == "__main__":
    generate_image("A beautiful sunset over mountains")
