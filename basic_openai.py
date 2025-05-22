import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()    
api_key = os.getenv("OPENAI_API_KEY")
    
client = OpenAI(api_key=api_key)

completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]
    )
    
print(completion.choices[0].message)