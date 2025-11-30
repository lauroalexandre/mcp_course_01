"""Lista os modelos Gemini disponiveis"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY", "")
genai.configure(api_key=google_api_key)

print("Modelos Gemini disponiveis:")
print("-" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"Nome: {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Suporta: {', '.join(model.supported_generation_methods)}")
        print()
