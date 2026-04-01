from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hola"}]
)

print(resp.choices[0].message["content"])
