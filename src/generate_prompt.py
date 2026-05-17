import os
from groq import Groq

def generate_prompt():
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a professional photography prompt generator. Generate unique, detailed prompts for AI image generation featuring nature scenes with people. Focus on professional photography style, golden hour lighting, stunning landscapes."
            },
            {
                "role": "user",
                "content": "Generate ONE unique image prompt for today. Theme: breathtaking nature photography with a person. Include specific details about lighting, composition, camera angle, and mood. Keep it under 200 words. Return ONLY the prompt, nothing else."
            }
        ],
        max_tokens=300,
        temperature=1.0
    )
    
    prompt = response.choices[0].message.content.strip()
    return prompt

if __name__ == "__main__":
    print(generate_prompt())
