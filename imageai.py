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
rate_limiter = asyncio.Semaphore(1)  # Only 1 at a time

# === Encode image ===
def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding {image_path}: {e}")
        return None

# === Async call wrapper with rate limiting ===
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
                        "Respond in the following JSON format:\n\n"
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

    async with rate_limiter:
        await asyncio.sleep(1)  # Wait 1 second per allowed request
        try:
            response = client.chat.complete(model=model, messages=messages)
            content = response.choices[0].message.content.strip("`'\"").strip("json")
            print(image_path + " processed")
            return {"image": image_path, "data": json.loads(content)}
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
    image_paths = get_image_paths()
    tasks = [aicall_limited(path) for path in image_paths]
    results = await asyncio.gather(*tasks)

    clean_data = []

    for item in results:
        if "data" in item:
            data = item["data"]
            if isinstance(data, list):
                clean_data.extend(data)  # flatten list
            else:
                clean_data.append(data)

    with open("all_results.json", "w") as f:
        json.dump(clean_data, f, indent=4)

    print("✅ Done — Results saved to all_results.json")

start_time= time.time()
asyncio.run(main())

print("time taken:" + str(time.time()-start_time))
