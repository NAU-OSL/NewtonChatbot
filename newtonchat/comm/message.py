"""Defines a MessageContext"""
from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum



if TYPE_CHECKING:
    from ..bots.newton.states.state import StateDefinition
    from typing import Sequence, TypedDict

    from .kernelcomm import KernelComm
    from .chat_instance import ChatInstance

    class IOptionItem(TypedDict, total=False):
        """Defines an Option for a list of options"""
        key: str
        label: str

    class IFeedback(TypedDict):
        """Represents a message feedback"""
        rate: int
        reason: str
        otherreason: str

    class IChatMessage(TypedDict):
        """Represents a message"""
        id: str
        text: str
        type: str
        timestamp: int
        reply: str | None
        display: MessageDisplay
        kernelProcess: KernelProcess
        kernelDisplay: MessageDisplay

        feedback: IFeedback
        loading: bool
        alternatives: list[str]
        selectedAlt: int
        inConversationContext: bool


class MessageDisplay(IntEnum):
    """Represents a message display mode"""
    DEFAULT = 0
    HIDDEN = 1
    SUPERMODE_INPUT = 2


class KernelProcess(IntEnum):
    """Indicates whether or not the kernel should process the message"""
    PREVENT = 0
    PROCESS = 1
    FORCE = 2


@dataclass
class MessageContext:
    """Represents a message context"""

    comm: KernelComm
    instance: ChatInstance
    original_message: IChatMessage

    @staticmethod
    def create_message(
        text: str | list[str],
        type_: str,
        reply: str | None = None,
        display: MessageDisplay = MessageDisplay.DEFAULT,
        in_conversation_context: bool = False,
    ) -> IChatMessage:
        """Creates IChatMessage"""
        alternatives = []
        selected_alt = -1
        if isinstance(text, list):
            alternatives = text
            text = text[0]
            selected_alt = 0
        return {
            "id": str(uuid.uuid4()),
            "text": text,
            "type": type_,
            "timestamp": int(datetime.timestamp(datetime.now())*1000),
            "reply": reply,
            "display": display,
            "kernelProcess": KernelProcess.PREVENT,
            "kernelDisplay": MessageDisplay.DEFAULT,
            "feedback": {
                "rate": 0,
                "reason": "",
                "otherreason": "",
            },
            "loading": False,
            "alternatives": alternatives,
            "selectedAlt": selected_alt,
            "inConversationContext": in_conversation_context,
        }

    @property
    def text(self):
        """Returns original message text"""
        return self.original_message['text']

    def reply(self, text: str | list[str],
                type_: str="bot",
                checkpoint: StateDefinition | None = None,
                in_conversation_context: bool = False):
        """Reply indicating the reply_to field"""
        message = self.create_message(
            text,
            type_,
            self.original_message['id'],
            self.original_message['kernelDisplay'],
            in_conversation_context
        )
        if checkpoint is not None:
            self.instance.checkpoints[message['id']] = checkpoint
        self.instance.reply_message(message)

    def reply_options(
        self,
        options: Sequence[IOptionItem],
        type_: str="bot",
        ordered: bool = True,
        full: bool = False,
        checkpoint: StateDefinition | None = None,
        text: str | None = None
    ):
        """Reply list of options"""
        # pylint: disable=consider-using-f-string
        mode = 'ol' if ordered else 'ul'
        if full:
            mode = 'f' + mode

        result = []
        for option in options:
            result.append("{key}::bot::{label}".format(**option))
        reply_text = f'####{mode}#:\n-' + '\n-'.join(result)

        if text is not None:
            reply_text = text + '\n' + reply_text
        self.reply(reply_text, type_, checkpoint=checkpoint)

    def getattr(self, attr_name):
        """Use dot notation to get message attribute"""
        if attr_name in self.original_message:
            return self.original_message[attr_name]

        return None
