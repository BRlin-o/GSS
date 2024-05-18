import boto3
from langchain.agents import Tool
from langchain_aws import BedrockChat
from config import config
from rag import get_rag_chain

from dotenv import load_dotenv
load_dotenv()

# model_id = config["models"]["Claude 3 Sonnet"]["model_id"]
model_config = config["models"]["llama3 70B"]
# kb_id = config["rags"]["JEGO"]["knowledge_base_id"]
kb_id="PM7KE9I1CP"

bedrock_runtime = boto3.client("bedrock-runtime")

claude_llm = BedrockChat(
    model_id=model_config["model_id"],
    # model_kwargs={"max_tokens": 500, "temperature": 0.0},
    model_kwargs={"max_gen_len": 500, "temperature": 0.0},
)

rag_qa_chain = get_rag_chain(kb_id, claude_llm)

def call_rag(query):
    print("[DEBUG] call_rag: query=", query)
    return rag_qa_chain({"question": query})

LLM_AGENT_TOOLS = [
    Tool(
        name="Search",
        # func=lambda query: rag_qa_chain({"question": query}),
        func=call_rag,
        description=(
            "Use when you are asked questions about the Gogoro scooter model. "
            "Ensure the input query includes the scooter model information, such as: "
            "'CrossOver', 'Delight', 'JEGO', 'SuperSport', 'VIVA MIX', 'VIVA XL', 'VIVA', 'S1', 'S2', 'S3'."
            " The query should be a well-formatted question that clearly specifies the scooter model."
        ),
    )
]