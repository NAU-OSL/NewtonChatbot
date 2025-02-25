"""Defines gpt bot"""
from __future__ import annotations

import traceback
import json

from typing import TYPE_CHECKING

import openai

from ..comm.message import MessageContext

if TYPE_CHECKING:
    from ..comm.chat_instance import ChatInstance


class ChatGPTBot:
    """GPT bot that connects to Open AI"""

    def __init__(self):
        self.prompt = ""
        self.api_key = ""
        self.model_config = {}
        self.rules_to_be_followed = ""
        self.context_window = 0

    @classmethod
    def config(cls):
        """Defines configuration inputs for bot"""
        return {
            "prompt": ('textarea', {"value": "", "rows": 6}),
            "rules_to_be_followed": ('textarea', {"value": "", "rows": 6}),
            "model": ('datalist', {"value": "gpt-3.5-turbo-0301", "options": [
                'gpt-3.5-turbo-0301',
                'gpt-3.5-turbo',
                'gpt-4'
            ]}),
            "temperature": ('range', {"value": 1, "min": 0, "max": 1, "step": 0.01}),
            "max_tokens": ('range', {"value": 1024, "min": 1, "max": 4000, "step": 1}),
            "top_p": ('range', {"value": 0.9, "min": 0, "max": 1, "step": 0.01}),
            "frequency_penalty": ('range', {"value": 0, "min": 0, "max": 2, "step": 0.01}),
            "presence_penalty": ('range', {"value": 0, "min": 0, "max": 2, "step": 0.01}),
            "n": ('range', {"value": 1, "min": 1, "max": 20, "step": 1}),
            "api_key": ("file", {"value": ""}),
        }

    def config_values(self):
        """Returns current instance config values"""
        return {
            "prompt": self.prompt,
            "rules_to_be_followed": self.rules_to_be_followed,
            "model": self.model_config['model'],
            "temperature": self.model_config['temperature'],
            "max_tokens": self.model_config['max_tokens'],
            "top_p": self.model_config['top_p'],
            "frequency_penalty": self.model_config['frequency_penalty'],
            "presence_penalty": self.model_config['presence_penalty'],
            "n": self.model_config['n'],
            "api_key": self.api_key,
        }

    def _set_config(self, original, data, key, convert=str):
        """Sets config of model_config"""
        self.model_config[key] = convert(data.get(key, original[key]))

    def set_config(self, instance: ChatInstance, data: dict, start=False):
        """Initializes bot"""
        try:
            original = self.config()
            self.prompt = data.get("prompt", self.prompt)
            self.rules_to_be_followed = data.get("rules_to_be_followed", self.rules_to_be_followed)
            self.api_key = data.get("api_key", "").strip()
            self._set_config(original, data, 'model', str)
            self._set_config(original, data, 'temperature', float)
            self._set_config(original, data, 'max_tokens', int)
            self._set_config(original, data, 'top_p', float)
            self._set_config(original, data, 'frequency_penalty', float)
            self._set_config(original, data, 'presence_penalty', float)
            self._set_config(original, data, 'n', int)

            instance.config["enable_autocomplete"] = False

            if start:
                instance.history.append(MessageContext.create_message(
                    self.prompt, "system", in_conversation_context=True
                ))

                response_messages = self.get_response_messages(instance)

                instance.history.append(MessageContext.create_message(
                    response_messages,
                    "bot",
                    in_conversation_context=True
                ))

        except Exception:  # pylint: disable=broad-exception-caught
            instance.reply_message(MessageContext.create_message(traceback.format_exc(), "error"))

    def refresh(self, instance: ChatInstance):
        """Refresh chatbot"""
        # pylint: disable=no-self-use
        instance.sync_chat("refresh")

    def process_message(self, context: MessageContext) -> None:
        """Processes user messages"""
        # pylint: disable=unused-argument
        try:
            response_messages = self.get_response_messages(context.instance)
            context.reply(
                response_messages,
                in_conversation_context=True
            )
        except Exception:  # pylint: disable=broad-exception-caught
            context.reply(traceback.format_exc(), "error")

    def process_autocomplete(self, instance: ChatInstance, request_id: int, query: str):
        """Processes user autocomplete query"""
        # pylint: disable=unused-argument
        # pylint: disable=no-self-use
        instance.send({
            "operation": "autocomplete-response",
            "responseId": request_id,
            "items": [],
        })

    def save(self):
        """Saves bot"""
        return {
            "config": self.model_config,
            "prompt": self.prompt,
            "rules_to_be_followed": self.rules_to_be_followed,
            "context_window": self.context_window,
            "!form": {
                "api_key": ("file", {"value": ""})
            }
        }

    def load(self, data):
        """Loads bot"""
        if "config" in data:
            self.model_config = {**self.model_config, **data["config"]}
        self.prompt = data.get("prompt", self.prompt)
        self.rules_to_be_followed = data.get("rules_to_be_followed", self.rules_to_be_followed)
        self.context_window = data.get("context_window", self.context_window)
        if form := data.get("!form", None):
            self.api_key = form.get("api_key", "").strip()


    def get_trimmed_message(self, message):
        """Removes metadata from message"""
        # pylint: disable=no-self-use
        return message.split('####metadata#:')[0].replace('####markdown#:\n', '')

    def get_response_messages(self, instance):
        """Send conversation context to ChatGPT and returns response messages"""
        # pylint: disable=broad-exception-raised
        openai.api_key = self.api_key

        conversation_context = []
        conversation_context_ids = []
        for pos, message in enumerate(instance.history):
            if message.get("inConversationContext", False):
                role = message["type"]
                if role == "bot":
                    role = "assistant"
                if role not in {"system", "user", "assistant"}:
                    continue

                position = str(pos)
                if message.get("selectedAlt", -1) == -1:
                    content = message["text"]
                else:
                    content = message["alternatives"][message["selectedAlt"]]
                    position += f'|{message["selectedAlt"]}'

                content = self.get_trimmed_message(content)
                if role == "user" and self.rules_to_be_followed:
                    content = f"{content} \\n {self.rules_to_be_followed}"
                    position += ':R'

                conversation_context_ids.append(position)
                conversation_context.append(
                    {
                        "role": role,
                        "content": content
                    }
                )
        response = openai.ChatCompletion.create(
            messages=conversation_context[self.context_window:],
            **self.model_config
        )

        if response.get("choices") is None or len(response["choices"]) == 0:
            raise Exception("GPT API returned no choices")

        response_messages = []

        total_tokens_used = response["usage"]["total_tokens"]

        if total_tokens_used > 3000:
            self.context_window += 1

        meta_json = json.dumps({
            "tokens": total_tokens_used,
            "context": conversation_context_ids,
            "context_window": self.context_window 
        })

        for response_choice in response["choices"]:
            message = getattr(response_choice, "message")
            content = getattr(message, "content").strip()

            response_messages.append(
                f"####markdown#:\n{content}\n####metadata#:{meta_json}")

        return response_messages
