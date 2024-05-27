import os
import boto3
import streamlit as st
from langchain.agents import Tool
from langchain_aws import BedrockChat
from config import config
from rag import get_rag_chain

from dotenv import load_dotenv
load_dotenv()

CAR_MODEL = "CrossOver"

# model_id = config["models"]["llama3 70B"]["model_id"]
model_id = config["models"]["Claude 3 Haiku"]["model_id"]
# kb_id = config["rags"]["JEGO"]["knowledge_base_id"]
kb_id = os.getenv("GOGORO_SEARCH_KNOWLEDGE_BASE_ID")

bedrock_runtime = boto3.client("bedrock-runtime")

claude_llm = BedrockChat(
    model_id=model_id,
    model_kwargs={
        # "max_seq_len": 1024, 
        "temperature": 0.0
    },
)

def call_search(query):
    global CAR_MODEL;
    CAR_MODEL = st.session_state["car_model"]
    super_query = f"{query}？"
    return get_rag_chain(kb_id, claude_llm, CAR_MODEL)(super_query)

LLM_AGENT_TOOLS = [
    Tool(
        name="GogoroSearch",
        func=lambda query: call_search(query),
        description=(
            "Use when you are asked any questions about Gogoro."
            " The Input should be a correctly formatted question, and using 繁體中文."
            " If the response contains any markdown syntax like `![]()`, please make sure to display it directly in the chat, as the frontend can render markdown to show image data."
        ),
    )
]

# LLM_AGENT_TOOLS = [
#     Tool(
#         name="CrossOver_Search",
#         func=lambda query: call_search(query),
#         description=(
#             "Use when you are asked any questions about Gogoro CrossOver."
#             " The Input should be a correctly formatted question."
#         ),
#     ),
#     Tool(
#         name="Delight_Search",
#         func=lambda query: get_rag_chain(kb_id, claude_llm, "Delight")(query),
#         description=(
#             "Use when you are asked any questions about Gogoro Delight."
#             " The Input should be a correctly formatted question."
#         ),
#     ),
#     Tool(
#         name="JEGO_Search",
#         func=lambda query: get_rag_chain(kb_id, claude_llm, "JEGO")(query),
#         description=(
#             "Use when you are asked any questions about Gogoro JEGO."
#             " The Input should be a correctly formatted question."
#         ),
#     ),
#     Tool(
#         name="SuperSport_Search",
#         func=lambda query: get_rag_chain(kb_id, claude_llm, "SuperSport")(query),
#         description=(
#             "Use when you are asked any questions about Gogoro SuperSport."
#             " The Input should be a correctly formatted question."
#         ),
#     ),
#     Tool(
#         name="VIVA_Search",
#         func=lambda query: get_rag_chain(kb_id, claude_llm, "VIVA")(query),
#         description=(
#             "Use when you are asked any questions about Gogoro VIVA."
#             " The Input should be a correctly formatted question."
#         ),
#     ),
#     Tool(
#         name="VIVA_XL_Search",
#         func=lambda query: get_rag_chain(kb_id, claude_llm, "VIVA Xl")(query),
#         description=(
#             "Use when you are asked any questions about Gogoro_VIVA_XL."
#             " The Input should be a correctly formatted question."
#         ),
#     ),
#     Tool(
#         name="VIVA_MIX_Search",
#         func=lambda query: get_rag_chain(kb_id, claude_llm, "VIVA Mix")(query),
#         description=(
#             "Use when you are asked any questions about Gogoro_VIVA_MIX."
#             " The Input should be a correctly formatted question."
#         ),
#     ),
# ]