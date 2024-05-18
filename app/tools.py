import boto3
from langchain.agents import Tool
from langchain_aws import BedrockChat
from config import config
from rag import get_rag_chain

from dotenv import load_dotenv
load_dotenv()

# model_id = config["models"]["llama3 70B"]["model_id"]
model_id = config["models"]["Claude 3 Haiku"]["model_id"]
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

# rag_qa_chain = get_rag_chain(kb_id, claude_llm)

# def call_rag(query):
#     print("[DEBUG] Query: ", query)
#     _query = query.split("Observation")[0]
#     return rag_qa_chain({"question": f"使用中文回應此問題。{_query}"})

LLM_AGENT_TOOLS = [
    Tool(
        name="CrossOver_Search",
        func=lambda query: get_rag_chain(kb_id, claude_llm, "CrossOver")(query),
        description=(
            "Use when you are asked any questions about Gogoro CrossOver."
            " The Input should be a correctly formatted question."
        ),
    ),
    Tool(
        name="Delight_Search",
        func=lambda query: get_rag_chain(kb_id, claude_llm, "Delight")(query),
        description=(
            "Use when you are asked any questions about Gogoro Delight."
            " The Input should be a correctly formatted question."
        ),
    ),
    Tool(
        name="JEGO_Search",
        func=lambda query: get_rag_chain(kb_id, claude_llm, "JEGO")(query),
        description=(
            "Use when you are asked any questions about Gogoro JEGO."
            " The Input should be a correctly formatted question."
        ),
    ),
    Tool(
        name="SuperSport_Search",
        func=lambda query: get_rag_chain(kb_id, claude_llm, "SuperSport")(query),
        description=(
            "Use when you are asked any questions about Gogoro SuperSport."
            " The Input should be a correctly formatted question."
        ),
    ),
    Tool(
        name="VIVA_Search",
        func=lambda query: get_rag_chain(kb_id, claude_llm, "VIVA")(query),
        description=(
            "Use when you are asked any questions about Gogoro VIVA."
            " The Input should be a correctly formatted question."
        ),
    ),
    Tool(
        name="VIVA_XL_Search",
        func=lambda query: get_rag_chain(kb_id, claude_llm, "VIVA Xl")(query),
        description=(
            "Use when you are asked any questions about Gogoro VIVA XL."
            " The Input should be a correctly formatted question."
        ),
    ),
    Tool(
        name="VIVA_MIX_Search",
        func=lambda query: get_rag_chain(kb_id, claude_llm, "VIVA Mix")(query),
        description=(
            "Use when you are asked any questions about Gogoro VIVA MIX."
            " The Input should be a correctly formatted question."
        ),
    ),
]