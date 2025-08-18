import os
import json
import requests
from groq import Groq
from search.utils import scrape_metadata

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
    chat_context=[],
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

    chat_context_plus_prompt = [*chat_context, {"role": "user", "content": content_parts}]
    json.dump(chat_context_plus_prompt, open("final_prompt.json", "w"), indent=4)

    data = {
        "model": model,
        "messages": chat_context_plus_prompt,
        "return_images": return_images,
        "search_mode": search_mode,
        "return_related_questions": True,
        **extra_kwargs
    }

    response = requests.post(url, json=data, headers=HEADERS)
    print("Calling:", url)
    print("Payload:", data)
    print("Response:", response.text)

    if response.status_code == 200:
        response_dict = response.json()
        if "search_results" in response_dict:
            citations_metadata = []
            for search_result in response_dict["search_results"]:
                citations_metadata.append(scrape_metadata(search_result))

            response_dict["citations_metadata"] = citations_metadata

        return response_dict
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
