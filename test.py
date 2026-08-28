from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic
import os

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("ANTHROPIC_BASE_URL")
)

message = client.messages.create(
    model="claude-sonnet-4.6",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Say hello in one sentence."
        }
    ]
)

print(message.content[0].text)