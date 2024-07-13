from openai import OpenAI
import json, os

class GptClient():
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
        )

    def call_with_prompt(self, prompt: str):
        response = self.client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        seed=42,
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": "Transfer 1 btc to Tony"},
            {"role": "assistant", "content": json.dumps({
                    "transaction": "transfer",
                    "amount": 1,
                    "currency": "BTC",
                    "to": "Tony",
                    "note": "Transfer 3 BTC to Tony"
                })
            },
            {"role": "user", "content": f"{prompt}"},
            
        ]
        )
        return response
    
    def call_with_prompt_normal(self, prompt: str):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}"},
            ]
        )
        return response
