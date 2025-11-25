"""
Simple AI engine for MVP.
- Uses the stored business_text and a light templated reply generator.
- Optional: If you have OpenAI API key, uncomment the call to OpenAI for better replies.
"""
import os
from typing import Optional
from dotenv import load_dotenv


load_dotenv()


OPENAI_KEY = os.getenv('OPENAI_API_KEY')
USE_OPENAI = bool(OPENAI_KEY)


async def generate_reply(business_text: str, user_message: str) -> str:
# Very small retrieval-style prompt: combine business_text and message
prompt = (
f"You are a customer support assistant for this business:\n{business_text}\n\n"
f"Customer: {user_message}\nAssistant:")


if USE_OPENAI:
# Example using OpenAI's HTTP API with httpx (user supplies API key)
import httpx
headers = {'Authorization': f'Bearer {OPENAI_KEY}'}
data = {
'model': 'gpt-4o-mini',
'messages': [
{'role': 'system', 'content': 'You are a helpful assistant that replies concisely'},
{'role': 'user', 'content': prompt}
],
'max_tokens': 250
}
async with httpx.AsyncClient(timeout=30) as client:
res = await client.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers)
r = res.json()
try:
return r['choices'][0]['message']['content'].strip()
except Exception:
return "Sorry, I couldn't generate a reply right now."


# Fallback: simple template-based reply
reply = (
f"Hello! Thanks for your message. Based on the business info I have, here's a helpful reply:\n\n"
f"{business_text[:500]}...\n\nResponse to your message: {user_message}\n\n"
f"If you'd like more details or want a human to follow up, say 'talk to human'."
)
return reply
