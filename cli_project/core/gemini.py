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
        # Se for uma lista de tool results, converte para formato Gemini
        if isinstance(message, list) and len(message) > 0:
            if isinstance(message[0], dict) and message[0].get("type") == "tool_result":
                # Converte tool results para formato texto por enquanto
                # O Gemini espera function responses em formato específico
                tool_results_text = "\n".join([
                    f"Tool {tr.get('tool_use_id', 'unknown')}: {tr.get('content', '')}"
                    for tr in message
                ])
                user_message = {
                    "role": "user",
                    "content": tool_results_text
                }
                messages.append(user_message)
                return

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

    def _convert_json_schema_to_gemini(self, json_schema):
        """Converte JSON Schema para o formato do Gemini"""
        if not json_schema:
            return {}

        # Remove campos não suportados pelo Gemini
        gemini_schema = {}
        if "type" in json_schema:
            gemini_schema["type_"] = json_schema["type"].upper()

        if "properties" in json_schema:
            properties = {}
            for prop_name, prop_schema in json_schema["properties"].items():
                prop_def = {}
                if "type" in prop_schema:
                    prop_def["type_"] = prop_schema["type"].upper()
                if "description" in prop_schema:
                    prop_def["description"] = prop_schema["description"]
                properties[prop_name] = prop_def
            gemini_schema["properties"] = properties

        if "required" in json_schema:
            gemini_schema["required"] = json_schema["required"]

        return gemini_schema

    def _convert_tools_to_gemini_format(self, tools):
        """Converte tools do formato MCP para o formato do Gemini"""
        if not tools:
            return None

        gemini_tools = []
        for tool in tools:
            # Converte o schema de parâmetros
            parameters_schema = self._convert_json_schema_to_gemini(tool["input_schema"])

            # Gemini espera function declarations
            function_declaration = {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": parameters_schema
            }
            gemini_tools.append(function_declaration)

        return gemini_tools

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
        Envia mensagens para o Gemini e retorna a resposta com suporte a tools
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

        # Converte tools para o formato Gemini
        gemini_tools = None
        if tools:
            gemini_tools = self._convert_tools_to_gemini_format(tools)

        # Cria o modelo com instruções do sistema e tools
        model_kwargs = {"model_name": self.model_name}
        if system:
            model_kwargs["system_instruction"] = system
        if gemini_tools:
            model_kwargs["tools"] = gemini_tools

        model = genai.GenerativeModel(**model_kwargs)

        # Inicia o chat
        chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])

        # Envia a última mensagem
        last_message = gemini_messages[-1]["parts"][0] if gemini_messages else ""
        response = chat.send_message(
            last_message,
            generation_config=generation_config
        )

        # Verifica se há function calls na resposta
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        # Gemini está solicitando uma tool call
                        return self._convert_function_call_to_message(part.function_call)

        # Resposta de texto normal
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

    def _convert_function_call_to_message(self, function_call):
        """Converte function call do Gemini para formato compatível com tool_use"""
        # Extrai argumentos do function call
        args = {}
        if hasattr(function_call, 'args'):
            args = dict(function_call.args)

        # Cria conteúdo no formato esperado pelo ToolManager
        content = [{
            "type": "tool_use",
            "id": f"call_{function_call.name}",  # Gemini não fornece ID, então criamos um
            "name": function_call.name,
            "input": args
        }]

        return GeminiMessage(content=content, stop_reason="tool_use")
