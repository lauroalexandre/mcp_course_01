"""Teste simples da integração com Gemini"""
import os
from dotenv import load_dotenv
from core.gemini import Gemini

load_dotenv()

gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
google_api_key = os.getenv("GOOGLE_API_KEY", "")

print(f"Testando modelo: {gemini_model}")
print(f"API Key configurada: {'Sim' if google_api_key else 'Nao'}")

# Testa a criação do serviço
gemini_service = Gemini(model=gemini_model, api_key=google_api_key)
print("[OK] Servico Gemini criado com sucesso")

# Testa uma mensagem simples
messages = [
    {"role": "user", "content": "Quanto e 1+1? Responda apenas com o numero."}
]

print("\nEnviando mensagem de teste...")
response = gemini_service.chat(messages=messages)
print(f"[OK] Resposta recebida: {gemini_service.text_from_message(response)}")
print(f"Stop reason: {response.stop_reason}")

print("\n[OK] Teste concluido com sucesso!")
