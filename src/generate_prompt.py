import os
import random
from groq import Groq

def generate_prompt():
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Random themes for variety
    themes = [
        "mountain landscape at golden hour",
        "ocean beach at sunrise",
        "autumn forest with falling leaves",
        "lavender fields in Provence",
        "snowy winter wonderland",
        "tropical rainforest with waterfall",
        "desert sand dunes at sunset",
        "cherry blossom garden in Japan",
        "northern lights in Iceland",
        "misty morning in tea plantations",
        "wildflower meadow in spring",
        "rocky coastline with dramatic waves",
        "bamboo forest path",
        "alpine lake with reflections",
        "sunflower field at golden hour"
    ]
    
    # Random person types
    persons = [
        "a young woman in a flowing dress",
        "a solo traveler with a backpack",
        "a man in casual outdoor clothing",
        "a couple holding hands",
        "a woman in traditional local attire",
        "a photographer with a camera",
        "a person meditating peacefully",
        "a woman with long hair blowing in wind",
        "an adventurer looking at the view",
        "a person walking alone on a path"
    ]
    
    # Random photography styles
    styles = [
        "National Geographic photography style",
        "cinematic movie still",
        "fine art portrait photography",
        "editorial fashion photography",
        "dreamy ethereal aesthetic",
        "moody atmospheric photography",
        "vibrant travel photography",
        "minimalist composition",
        "romantic golden hour portrait",
        "dramatic landscape photography"
    ]
    
    theme = random.choice(themes)
    person = random.choice(persons)
    style = random.choice(styles)
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """You are an expert AI image prompt engineer. 
                You create detailed, professional prompts for stunning photography.
                Your prompts always include: subject, environment, lighting, mood, camera details, and style.
                You make each prompt unique and visually striking."""
            },
            {
                "role": "user",
                "content": f"""Create ONE detailed image generation prompt combining:
                
Theme: {theme}
Person: {person}  
Style: {style}

Requirements:
- Professional photography quality
- Specific lighting details (golden hour, soft light, etc.)
- Camera specs (85mm lens, shallow depth of field, etc.)
- Mood and atmosphere
- Rich colors and composition details
- 8K, ultra realistic, highly detailed

Return ONLY the prompt text, nothing else. Make it under 150 words."""
            }
        ],
        max_tokens=300,
        temperature=1.2
    )
    
    prompt = response.choices[0].message.content.strip()
    return prompt

if __name__ == "__main__":
    print(generate_prompt())
