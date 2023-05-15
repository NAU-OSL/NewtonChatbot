"""Define a chat instance"""
from __future__ import annotations
from collections import defaultdict
import traceback
import weakref
from typing import TYPE_CHECKING, Any, cast

from ..loader import LOADERS
from .message import KernelProcess, MessageContext

if TYPE_CHECKING:
    from ..bots.newton.states.state import StateDefinition
    from .kernelcomm import KernelComm
    from .message import IChatMessage
else:
    IChatMessage = None


def apply_partial(original: dict, update: dict):
    """Apply nested changes to original dict"""
    for key, value in update.items():
        if isinstance(value, dict):
            apply_partial(original[key], value)
        else:
            original[key] = value


class ChatInstance:
    """Chat Instance handler"""

    def __init__(self, comm: KernelComm, chat_name: str, mode="newton"):
        self.mode = mode
        self.comm_ref = weakref.ref(comm)
        self.bot_loader = LOADERS[mode](comm)
        self.memory: dict[str, Any] = defaultdict(lambda: None)

        self.chat_name = chat_name

        self.history: list[IChatMessage] = []
        self.message_map: dict[str, IChatMessage] = {}
        self.config = {
            "process_in_kernel": True,
            "enable_autocomplete": True,
            "enable_auto_loading": False,
            "loading": False,
            "process_base_chat_message": True,

            "show_replied": False,
            "show_index": False,
            "show_time": True,
            "show_build_messages": True,
            "show_kernel_messages": True,
            "show_metadata": False,
            "direct_send_to_user": False,
            "show_extra_messages": False,
        }
        self.checkpoints: dict[str, StateDefinition | None] = {}

    @property
    def bot(self):
        """Returns current bot"""
        return self.bot_loader.current()

    def start_bot(self, data: dict):
        """Starts bot and sets history map"""
        self.bot.set_config(self, data, start=True)
        for message in self.history:
            self.message_map[message['id']] = message
        return self

    def info(self):
        """Return chat instance info"""
        return {
            "mode": self.mode,
            "history": self.history,
            "config": self.config,
            "bot_config": self.bot.config_values(),
            "bot_config_loader": self.bot.config(),
        }

    def sync_chat(self, operation):
        """Sends message with history and general config"""
        self.send({
            "operation": operation,
            **self.info()
        })

    def refresh(self):
        """Refreshes instance"""
        self.bot.refresh(self)
        self.sync_chat("refresh")

    def receive(self, data: dict[str, Any]):
        """Processes received requests"""
        try:
            operation: str = data.get("operation", "")
            if operation == "message":
                message: IChatMessage = cast(IChatMessage, data.get("message"))
                self.receive_message(message)
            elif operation == "refresh":
                self.refresh()
            elif operation == "autocomplete-query":
                self.receive_autocomplete_query(
                    data.get('requestId'),
                    data.get('query')
                )
            elif operation == "config":
                key = data["key"]
                value = data["value"]
                if data["_mode"] == "update" or key not in self.config:
                    self.config[key] = value
                self.send({
                    "operation": "update-config",
                    "config": {key: self.config[key]},
                })
            elif operation == "sync-message":
                partial_message = data["message"]
                message = self.message_map[partial_message["id"]]
                apply_partial(cast(dict[Any, Any], message), partial_message)
                self.send({
                    "operation": "update-message",
                    "message": message,
                })
            elif operation == "update-instance-bot":
                self.bot.set_config(self, data['data'], start=False)
                self.refresh()
        except Exception:  # pylint: disable=broad-except
            print(traceback.format_exc())
            self.send({
                "operation": "error",
                "command": operation,
                "message": traceback.format_exc(),
            })

    def receive_message(self, message: IChatMessage):
        """Receives message from user"""
        comm_ref = self.comm_ref()
        if not comm_ref:
            raise Exception("Missing comm reference")  # pylint: disable=broad-exception-raised
        self.history.append(message)
        self.message_map[message['id']] = message
        self.send({
            "operation": "reply",
            "message": message
        })
        process_message = (
            message.get('kernelProcess') == KernelProcess.PROCESS
            and self.config["process_in_kernel"]
            or message.get('kernelProcess') == KernelProcess.FORCE
        )

        if process_message:
            context = MessageContext(comm_ref, self, message)
            self.bot.process_message(context)

        replicate_other_instances = (
            self.chat_name == "base"
            and (
                process_message
                or message.get('kernelProcess') == KernelProcess.PROCESS
            )
        )
        if replicate_other_instances:
            for chat_name, instance in comm_ref.chat_instances.items():
                if chat_name != "base" and instance.config["process_base_chat_message"]:
                    instance.receive_message(message)


    def receive_autocomplete_query(self, request_id, query):
        """Receives query from user"""
        if self.config["enable_autocomplete"]:
            self.bot.process_autocomplete(self, request_id, query)
        else:
            self.send({
                "operation": "autocomplete-response",
                "responseId": request_id,
                "items": [],
            })

    def send(self, data):
        """Receives send results"""
        data["instance"] = self.chat_name
        self.comm_ref().comm.send(data)

    def reply_message(self, message: IChatMessage):
        """Replies IChatMessage to user"""
        self.history.append(message)
        self.message_map[message['id']] = message
        self.send({
            "operation": "reply",
            "message": message
        })

    def save(self):
        """Saves instance data"""
        return {
            "name": self.chat_name,
            "mode": self.mode,
            "bot": self.bot.save(),
            "history": self.history,
            "config": self.config
        }

    def load(self, data):
        """Loads instance data"""
        self.chat_name = data.get("name", self.chat_name)
        self.mode = data.get("mode", self.mode)
        if "bot" in data:
            self.bot.load(data["bot"])
        if "history" in data:
            self.history = data["history"]
            self.message_map = {}
            for message in self.history:
                self.message_map[message['id']] = message
        self.config = {**self.config, **data.get("config", {})}
