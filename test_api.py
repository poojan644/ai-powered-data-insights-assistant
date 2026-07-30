import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
key = os.getenv("ANTHROPIC_API_KEY")
print("Key found:", key is not None)
print("Key prefix:", key[:15])

client = Anthropic(api_key=key)

try:
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=20,
        messages=[
            {"role": "user", "content": "Hello"}
        ],
    )
    print(response.content[0].text)

except Exception as e:
    print(type(e).__name__)
    print(e)