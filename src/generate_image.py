import requests
import urllib.parse
import time

def generate_image(prompt):
    print("Using Pollinations AI (free, no API key)...")
    
    # Clean and encode the prompt
    clean_prompt = prompt.replace('"', '').replace('\n', ' ').strip()
    encoded_prompt = urllib.parse.quote(clean_prompt[:500]) # Limit length
    
    # Pollinations AI URL
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
    
    print(f"Requesting image...")
    print(f"URL: {image_url[:100]}...")
    
    # Try multiple times
    for attempt in range(3):
        try:
            print(f"Attempt {attempt + 1}...")
            response = requests.get(image_url, timeout=180)
            
            if response.status_code == 200 and len(response.content) > 10000:
                with open("generated_image.png", "wb") as f:
                    f.write(response.content)
                print("Image generated successfully!")
                return "generated_image.png"
            else:
                print(f"Bad response: {response.status_code}, size: {len(response.content)}")
                time.sleep(10)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)
    
    raise Exception(f"Image generation failed after 3 attempts")

if __name__ == "__main__":
    generate_image("A beautiful sunset over mountains")
