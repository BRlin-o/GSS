import boto3
from langchain.agents import Tool
from langchain_aws import BedrockChat
from config import config
from rag import get_rag_chain

from dotenv import load_dotenv
load_dotenv()

model_id = config["models"]["Claude 3 Sonnet"]["model_id"]
kb_id = config["rags"]["JEGO"]["knowledge_base_id"]

bedrock_runtime = boto3.client("bedrock-runtime")

claude_llm = BedrockChat(
    model_id=model_id,
    model_kwargs={"max_tokens_to_sample": 500, "temperature": 0.0},
)

rag_qa_chain = get_rag_chain(kb_id, claude_llm)

LLM_AGENT_TOOLS = [
    Tool(
        name="JEGOSearch",
        func=lambda query: rag_qa_chain({"question": query}),
        description=(
            "Use when you are asked questions about Gogoro JEGO."
            " The Input should be a correctly formatted question."
        ),
    )
]