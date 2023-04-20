"""Defines gpt bot"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ..comm.message import MessageContext

if TYPE_CHECKING:
    from ..comm.chat_instance import ChatInstance


class ChatGPTBot:
    """GPT bot that connects to Open AI"""

    try:
        import json

        import os

        prompt_config = ""

        # Load Credentials
        with open("newtonchat\\bots\\chatgpt_config.json", "r") as f:
            prompt_config = json.load(f)

        base_prompt = prompt_config["base_prompt"]

    except Exception as e:
        base_prompt = ""

    def __init__(self):
        self.prompt = self.base_prompt
        self.api_key = ""
        self.model_config = {}
        self.conversation_context = [
            {"role": "system", "content": self.prompt}]

    @classmethod
    def config(cls):
        """Defines configuration inputs for bot"""
        return {
            "prompt": ('textarea', {"value": cls.base_prompt, "rows": 6}),
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

    def _set_config(self, original, data, key, convert=str):
        """Sets config"""
        self.model_config[key] = convert(data.get(key, original[key]))

    def start(self, instance: ChatInstance, data: dict):
        """Initializes bot"""
        try:
            import openai
            original = self.config()
            self.prompt = data.get("prompt", self.prompt)
            self.api_key = data.get("api_key", "").strip()
            self._set_config(original, data, 'model', str)
            self._set_config(original, data, 'temperature', float)
            self._set_config(original, data, 'max_tokens', int)
            self._set_config(original, data, 'top_p', float)
            self._set_config(original, data, 'frequency_penalty', float)
            self._set_config(original, data, 'presence_penalty', float)
            self._set_config(original, data, 'n', int)

            instance.config["enable_autocomplete"] = False

            if self.base_prompt != self.prompt:
                self.conversation_context = []
                self.attach_prompt_message("system", self.prompt)

            response_messages = self.get_response_messages()

            self.attach_prompt_message(
                "assistant", self.get_trimmed_message(response_messages[0]))

            for message_content in response_messages:
                instance.history.append(MessageContext.create_message(
                    (message_content),
                    "bot",
                    isGPTMessage=True
                ))

        except Exception:
            print("Exception")

    def refresh(self, instance: ChatInstance):
        """Refresh chatbot"""
        # pylint: disable=no-self-use
        instance.sync_chat("refresh")

    def process_message(self, context: MessageContext) -> None:
        """Processes user messages"""
        # pylint: disable=unused-argument

        try:
            if context.getattr('isGPTMessage'):
                self.attach_prompt_message(
                    "assistant", self.get_trimmed_message(context.text))

                context.instance.config['conversation_context_updated'] = self.conversation_context

                context.reply('GPT_message_block' +
                              self.conversation_context[-1]["content"])

            elif context.getattr('isUserPrompt'):
                conv_context = self.attach_prompt_message(
                    "user",  self.get_trimmed_message(context.text))

                context.reply('User_prompt_block:::before' +
                              self.conversation_context[-1]["content"])

                response_messages = self.get_response_messages()

                for message_content in response_messages:
                    context.reply(message_content, isGPTMessage=True)

                context.reply('User_prompt_block:::after' +
                              self.conversation_context[-1]["content"])

                # context.instance.config['conversation_context_updated'] = self.conversation_context

        except Exception:
            import traceback
            context.reply(traceback.format_exc(), "error")

        return self

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
            "!form": {
                "api_key": ("file", {"value": ""})
            }
        }

    def load(self, data):
        """Loads bot"""
        if "config" in data:
            self.model_config = {**self.model_config, **data["config"]}
        self.prompt = data.get("prompt", self.prompt)
        if form := data.get("!form", None):
            self.api_key = form.get("api_key", "").strip()

    def attach_prompt_message(self, role, content):
        if role == "user":
            rules = self.prompt_config["rules_to_be_followed"]

            content = f"{content} \\n {rules}"

        self.conversation_context.append(
            {
                "role": role,
                "content": content
            }
        )

        return self.conversation_context

    def get_trimmed_message(self, message):
        end = min(message.find('####metadata#:'), len(message))
        return message[0: end].replace('####markdown#:\n', '')

    def get_response_messages(self):
        # global total_tokens_used
        import openai
        import json
        openai.api_key = self.api_key

        response = openai.ChatCompletion.create(
            messages=self.conversation_context,
            **self.model_config
        )

        if response.get("choices") is None or len(response["choices"]) == 0:
            raise Exception("GPT API returned no choices")

        response_messages = []

        total_tokens_used = response["usage"]["total_tokens"]

        if total_tokens_used > 3000:
            self.conversation_context.pop()

        meta_json = json.dumps({"tokens": total_tokens_used})

        for response_choice in response["choices"]:
            message = getattr(response_choice, "message")

            content = getattr(message, "content").strip()

            self.attach_prompt_message("assistant", content)

            response_messages.append(
                f"####markdown#:\n{content}\n####metadata#:{meta_json}")

        return response_messages
