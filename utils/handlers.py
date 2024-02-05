from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.messages import BaseMessage
from langchain.schema import LLMResult
from typing import Dict, List, Any
from utils.logger import logging

class MyCustomHandler(BaseCallbackHandler):
    def __init__(self, queue) -> None:
        super().__init__()
        self._queue = queue
        self._stop_signal = None
        # print("Custom handler Initialized")
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self._queue.put(token)

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        logging.info("generation started")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        logging.info("\n\ngeneration concluded")
        self._queue.put(self._stop_signal)

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        logging.info("chat model started ")