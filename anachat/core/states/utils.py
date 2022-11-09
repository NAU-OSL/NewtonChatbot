"""State utility functions"""
import inspect
from functools import wraps
from typing import Iterable, Any, cast


from ...comm.context import MessageContext
from ..states.state import StateCallable, StateDefinition, StateGenerator

def statemanager(default: StateDefinition=True):
    """Wraps generator function to support waiting for user replies"""
    def inner(func: StateCallable | StateGenerator):
        """Inner decorator"""
        @wraps(func)
        def helper(context: MessageContext, *args, **kwargs) -> StateDefinition:
            if inspect.isgeneratorfunction(func):
                gen = func(context, *args, **kwargs)
                try:
                    next(gen)
                except StopIteration as exc:
                    return exc.value or default
                else:
                    return _GeneratorStateManager(gen)
            return cast(StateCallable, func)(context, *args, **kwargs) or default
        return helper
    return inner


class _GeneratorStateManager:
    """State for wrapping generator. Pass user messages to yield positions"""

    def __init__(self, gen):
        self.gen = gen

    def process_message(self, context: MessageContext) -> StateDefinition:
        """Processes user messages"""
        try:
            self.gen.send(context.text)
        except StopIteration as exc:
            return exc.value
        return self


class GoToState(Exception):
    """Exception that supports the redirection of states"""

    def __init__(self, state: StateDefinition, params: Iterable[Any] | None=None):
        self.state = state
        self.params = params or []
        super().__init__(
            f"This exception should be handled by AnaCore to go to {state}"
        )

def create_reply_state(text) -> StateCallable:
    """Create a state that when enacted replies a text"""
    @statemanager()
    def reply_state(context: MessageContext) -> StateDefinition:
        """Replies predefined text and returns to default state"""
        context.reply(text)
        return None
    return reply_state


def create_panel_state(url, title):
    """Create a state that when enacted opens a panel"""
    @statemanager()
    def panel_state(context: MessageContext) -> StateDefinition:
        """Opens a predefined panel and returns to default state"""
        context.comm.open_panel(url, title)
        return None
    return panel_state


def create_state_loader(state: StateDefinition):
    """Create a state that loads a state by name when enacted"""
    @statemanager()
    def state_loader(context: MessageContext) -> StateDefinition:
        raise GoToState(state)
    return state_loader
