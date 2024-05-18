import boto3
from langchain.agents import Tool
from langchain_aws import BedrockChat
from config import config
from rag import get_rag_chain

from dotenv import load_dotenv
load_dotenv()

model_id = config["models"]["llama3 70B"]["model_id"]
# kb_id = config["rags"]["JEGO"]["knowledge_base_id"]
kb_id = "TAQ9SHSXJD"

bedrock_runtime = boto3.client("bedrock-runtime")

claude_llm = BedrockChat(
    model_id=model_id,
    model_kwargs={
        # "max_seq_len": 1024, 
        "temperature": 0.0
    },
)

rag_qa_chain = get_rag_chain(kb_id, claude_llm)

def call_rag(query):
    print("[DEBUG] Query: ", query)
    _query = query.split("Observation")[0]
    return rag_qa_chain({"question": f"使用中文回應此問題。{_query}"})

LLM_AGENT_TOOLS = [
    Tool(
        name="Search",
        func=lambda query: call_rag(query),
        description=(
            "Use when you are asked any questions about Gogoro."
            " The Input should be a correctly formatted question."
        ),
    )
]