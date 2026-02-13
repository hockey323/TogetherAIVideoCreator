
import os
from together import Together
from dotenv import load_dotenv

load_dotenv()
client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

models = client.models.list()
print("Available Image Models:")
for m in models:
    if hasattr(m, 'type') and m.type and 'image' in m.type.lower():
        print(f"ID: {m.id}, Type: {m.type}")
