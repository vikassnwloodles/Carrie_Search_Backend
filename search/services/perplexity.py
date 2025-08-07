import os
import requests
from groq import Groq

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

BASE_URL = "https://api.perplexity.ai"


def call_perplexity_model(
    prompt=None,
    image_url=None,
    model="sonar-pro",
    return_images=False,
    search_mode="web",
    deep_research=False,
):
    url = f"{BASE_URL}/chat/completions"

    content_parts = []

    if prompt:
        content_parts.append({"type": "text", "text": prompt})

    if image_url and image_url != "undefined":
        content_parts.append({"type": "image_url", "image_url": {"url": image_url}})

    extra_kwargs = dict()
    if deep_research: extra_kwargs["reasoning_effort"] = "high"

    data = {
        "model": model,
        "messages": [{"role": "user", "content": content_parts}],
        "return_images": return_images,
        "search_mode": search_mode,
        **extra_kwargs
    }

    response = requests.post(url, json=data, headers=HEADERS)
    print("Calling:", url)
    print("Payload:", data)
    print("Response:", response.text)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text, "status": response.status_code}



client = Groq(
    api_key=GROQ_API_KEY,
)

# CALLING ONE OF THE MODEL VIA GROQ INFERENCE ENGINE
def call_groq_model(
    prompt=None,
    image_url=None,
    model="sonar-pro",
    return_images=False,
    search_mode="web",
    deep_research=False,
):
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return completion.to_dict()
