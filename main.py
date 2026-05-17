from src.generate_prompt import generate_prompt
from src.generate_image import generate_image
from src.upload_image import upload_image
from src.post_facebook import post_to_facebook

def main():
    print("🚀 Starting daily post automation...")
    
    # Step 1: Generate prompt
    print("📝 Generating image prompt...")
    prompt = generate_prompt()
    print(f"Prompt: {prompt[:100]}...")
    
    # Step 2: Generate image
    print("🎨 Generating image...")
    image_path = generate_image(prompt)
    print(f"Image saved: {image_path}")
    
    # Step 3: Upload image
    print("☁️ Uploading image...")
    image_url = upload_image(image_path)
    print(f"Image URL: {image_url}")
    
    # Step 4: Post to Facebook
    print("📱 Posting to Facebook...")
    caption = f"""🌿 Daily Nature Photography 🌿

✨ AI-Generated Art ✨

💬 Comment "PROMPT" to receive the prompt used to create this image!

#NaturePhotography #AIArt #DailyArt #Photography #Nature #Landscape #BeautifulDestinations #TravelPhotography #NatureLovers #ArtificialIntelligence"""
    
    result = post_to_facebook(image_url, caption)
    print(f"✅ Posted successfully! Post ID: {result}")
    
    # Save prompt for comment replies
    with open("last_prompt.txt", "w") as f:
        f.write(prompt)
    
    print("🎉 Done!")
    print(f"\n📋 Today's Prompt:\n{prompt}")

if __name__ == "__main__":
    main()
