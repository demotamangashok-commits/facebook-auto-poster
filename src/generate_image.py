import requests
import urllib.parse

def generate_image(prompt):
    print("Using Pollinations AI (free, no API key)...")
    
    # Encode the prompt for URL
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Pollinations AI - free image generation
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
    
    print(f"Requesting image...")
    
    # Download the image
    response = requests.get(image_url, timeout=120)
    
    if response.status_code == 200:
        with open("generated_image.png", "wb") as f:
            f.write(response.content)
        print("Image generated successfully!")
        return "generated_image.png"
    else:
        raise Exception(f"Image generation failed: {response.status_code}")

if __name__ == "__main__":
    generate_image("A beautiful sunset over mountains with a person")
