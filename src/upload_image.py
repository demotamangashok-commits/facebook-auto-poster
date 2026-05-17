import os
import base64
import requests

def upload_image(image_path):
    api_key = os.environ.get("IMGBB_API_KEY")
    
    with open(image_path, "rb") as file:
        image_data = base64.b64encode(file.read()).decode("utf-8")
    
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={
            "key": api_key,
            "image": image_data
        }
    )
    
    if response.status_code == 200:
        return response.json()["data"]["url"]
    else:
        raise Exception(f"Upload failed: {response.text}")

if __name__ == "__main__":
    print(upload_image("generated_image.png"))
