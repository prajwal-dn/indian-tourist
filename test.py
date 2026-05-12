import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

try:
    client = Groq(api_key=GROQ_API_KEY)
    result = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user", "content": "hello"}]
    )
    print("Response:", result.choices[0].message.content)
except Exception as e:
    print('ERROR:', e)
