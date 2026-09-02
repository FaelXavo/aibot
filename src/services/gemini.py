import httpx
import os

ai_model = "gemini-3.5-flash"
API_KEY = os.getenv("GEMINI_API_KEY")


async def ask_gemini(prompt :str):
    url = "https://generativelanguage.googleapis.com/v1beta/interactions"

    headers = {
		"x-goog-api-key": API_KEY,
		"Content-Type": "application/json"
	}

    data = {
		"model" : ai_model,
		"input" : prompt
	}

    async with httpx.AsyncClient(timeout=80) as client:
        response = await client.post(
			url,
			headers=headers,
			json=data,
		)

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    response.raise_for_status()

    return response.json()
