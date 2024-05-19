from typing import Dict, List, Union
from config import config

from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler
from langchain_core.messages import AIMessage, HumanMessage
from langchain.callbacks.manager import CallbackManager
from langchain_aws import BedrockChat
# from langchain.llms.bedrock import Bedrock
# import boto3

class ChatModel:
    def __init__(self, model_name: str, model_kwargs: Dict, callback_manager: CallbackManager = None, callbacks: List = None):
        self.model_config = config["models"][model_name]
        self.model_id = self.model_config["model_id"]
        self.model_kwargs = model_kwargs
        self.llm = BedrockChat(
            model_id=self.model_id, 
            model_kwargs=model_kwargs, 
            streaming=True,
            callback_manager=callback_manager, 
            callbacks=callbacks
        )

    def format_prompt(self, prompt: str) -> Union[str, List[Dict]]:
        """
        Format the input prompt according to the model's requirements.
        """
        model_config = self.model_config
        if model_config.get("input_format") == "text":
            return prompt
        elif model_config.get("input_format") == "list_of_dicts":
            prompt_text = {"type": "text", "text": prompt}
            return [prompt_text]
        else:
            raise ValueError(f"Unsupported input format for model: {self.model_id}")
