import google.generativeai as genai
from typing import Any, Dict, List


class GeminiMessage:
    """Wrapper para mensagens do Gemini para compatibilidade"""
    def __init__(self, content: Any, stop_reason: str = "end_turn"):
        self.content = content if isinstance(content, list) else [{"type": "text", "text": str(content)}]
        self.stop_reason = stop_reason


class Gemini:
    def __init__(self, model: str, api_key: str):
        genai.configure(api_key=api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)

    def add_user_message(self, messages: list, message):
        if isinstance(message, GeminiMessage):
            content = self._extract_text_from_content(message.content)
        else:
            content = message if isinstance(message, str) else str(message)

        user_message = {
            "role": "user",
            "content": content
        }
        messages.append(user_message)

    def add_assistant_message(self, messages: list, message):
        if isinstance(message, GeminiMessage):
            content = self._extract_text_from_content(message.content)
        else:
            content = message if isinstance(message, str) else str(message)

        assistant_message = {
            "role": "assistant",
            "content": content
        }
        messages.append(assistant_message)

    def _extract_text_from_content(self, content):
        """Extrai texto do formato de conteúdo"""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif "text" in block:
                        text_parts.append(block["text"])
            return "\n".join(text_parts) if text_parts else ""
        return str(content)

    def text_from_message(self, message: GeminiMessage) -> str:
        """Extrai texto de uma mensagem Gemini"""
        return self._extract_text_from_content(message.content)

    def _convert_messages_to_gemini_format(self, messages: List[Dict]) -> List[Dict]:
        """Converte mensagens para o formato do Gemini"""
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            content = msg["content"]

            if isinstance(content, list):
                text_content = self._extract_text_from_content(content)
            else:
                text_content = content

            gemini_messages.append({
                "role": role,
                "parts": [text_content]
            })
        return gemini_messages

    def chat(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop_sequences=[],
        tools=None,
        thinking=False,
        thinking_budget=1024,
    ) -> GeminiMessage:
        """
        Envia mensagens para o Gemini e retorna a resposta

        Nota: O Gemini não suporta nativamente tools no mesmo formato do Claude,
        então essa funcionalidade seria limitada ou precisaria de adaptação
        """
        # Converte mensagens para o formato Gemini
        gemini_messages = self._convert_messages_to_gemini_format(messages)

        # Configura parâmetros de geração
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": 8000,
        }

        if stop_sequences:
            generation_config["stop_sequences"] = stop_sequences

        # Prepara o prompt do sistema se fornecido
        if system:
            system_instruction = system
        else:
            system_instruction = None

        # Cria o modelo com instruções do sistema se fornecido
        if system_instruction:
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction
            )
        else:
            model = self.model

        # Inicia o chat
        chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])

        # Envia a última mensagem
        last_message = gemini_messages[-1]["parts"][0] if gemini_messages else ""
        response = chat.send_message(
            last_message,
            generation_config=generation_config
        )

        # Converte a resposta para o formato compatível
        response_text = response.text

        # Determina o stop_reason
        stop_reason = "end_turn"
        if hasattr(response, 'candidates') and response.candidates:
            finish_reason = response.candidates[0].finish_reason
            if finish_reason == 1:  # STOP
                stop_reason = "end_turn"
            elif finish_reason == 2:  # MAX_TOKENS
                stop_reason = "max_tokens"

        return GeminiMessage(content=response_text, stop_reason=stop_reason)
