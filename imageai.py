import json
import base64
import os
import time
import asyncio
from mistralai import Mistral
from functools import partial

# === Load API Key ===
with open('logins/aiapi.txt', 'r') as file:
    lines = file.readlines()
    api_key = lines[1].split(':', 1)[1].strip()

# === Initialize Mistral ===
model = "mistral-medium-latest"
client = Mistral(api_key=api_key)

# === Global rate limiter ===
rate_queue = asyncio.Queue()

async def rate_limiter_loop(queue):
    while True:
        await queue.put(True)
        await asyncio.sleep(1)


# === Encode image ===
def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding {image_path}: {e}")
        return None

async def aicall_limited(image_path):
    base64_image = encode_image(image_path)
    if not base64_image:
        return {"image": image_path, "error": "Encoding failed"}

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "This image is of a ballot which has been filled in. Return the REG ID number and the vote ID number for each product. "
                        "Only return the reg_id number, id letter, and vote id number."
                        "the vote id should always be 3 digits no matter what. If you there is a partial id, fill the slot with a 0."
                        "Respond in the following JSON format:\n"
                        '{ "reg_id": "12456", "id_letter": "A", "vote_id": "123"}\n'
                        "Do not include any extra explanation or commentary—just output a valid JSON only."
                    )
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                }
            ]
        }
    ]

    await rate_queue.get()  # Wait for rate limiter token

    try:
            response = await asyncio.to_thread(client.chat.complete, model=model, messages=messages)
            content = response.choices[0].message.content.strip("`'\"").strip("json")
            data = json.loads(content)

            # Save to file
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join("output_folder", f"{image_name}.json")
            with open(output_path, "w") as f:
                json.dump(data, f, indent=4)

            print(image_name + "Proccesed")

            return {"image": image_path, "data": data}

    except Exception as e:
        return {"image": image_path, "error": str(e)}
    
    
# === Load all images ===
def get_image_paths(folder="images"):
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

# === Main async runner ===
async def main():
    os.makedirs("output_folder", exist_ok=True)

    # Start the rate limiter loop in the background
    asyncio.create_task(rate_limiter_loop(rate_queue))

    image_paths = get_image_paths()
    tasks = [aicall_limited(path) for path in image_paths]

    await asyncio.gather(*tasks)

    print("✅ Done — Individual JSON files saved to 'output/'")



