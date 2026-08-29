import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("ANTHROPIC_API_KEY")
print(f"Key loaded: {key[:20]}..." if key else "Key NOT loaded")
print(f"Key length: {len(key) if key else 0}")