import base64
import random
from io import BytesIO
import os
from typing import List, Tuple, Union, Dict
import boto3
import tempfile

import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationChain, ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.agents import AgentExecutor, create_react_agent

from PIL import Image, UnidentifiedImageError
import pdfplumber

from config import config
from models import ChatModel
from prompts import CLAUDE_AGENT_PROMPT
from tools import LLM_AGENT_TOOLS

from dotenv import load_dotenv
load_dotenv()


INIT_MESSAGE = {
    "role": "assistant",
    "content": "尊貴的車主您好，我是您專屬的Gogoro Smart Scooter萬事通，很高興為您解答任何關於Gogoro的問題。",
}

class StreamHandler(BaseCallbackHandler):
    """
    Callback handler to stream the generated text to Streamlit.
    """

    def __init__(self, container: st.container, initial_text: str="") -> None:
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        Append the new token to the text and update the Streamlit container.
        """
        self.text += token
        self.container.markdown(self.text)


def set_page_config() -> None:
    """
    Set the Streamlit page configuration.
    """
    st.set_page_config(page_title="Chat with GSS", page_icon="🏍️", layout="wide")

def render_chat_interface():
    st.title("🏍️ Gogoro Smart Scooter 萬事通")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            car_model = st.selectbox("車型", ["JEGO", "CrossOver"])
            st.session_state["car_model"] = car_model
        with col2:
            chat_lang = st.selectbox("語言", ["繁體中文", "English"])
            st.session_state["chat_lang"] = chat_lang
    return car_model, chat_lang

def render_sidebar() -> Tuple[Dict, int, str]:
    """
    Render the sidebar UI and return the inference parameters.
    """
    with st.sidebar:
        with st.expander("LLM Settings"):
            model_name_select = st.selectbox(
                'Model',
                list(config["models"].keys()),
                key=f"{st.session_state['widget_key']}_Model_Id",
            )
            
            role_select = st.selectbox(
                'Role',
                # ["Default", "Translator", "Writer", "Custom"],
                list(config["prompts"].keys()),
                key=f"{st.session_state['widget_key']}_role_Id",
            )
            # Set the initial value of the text area based on the selected role
            st.session_state["role_prompt"] = config["prompts"].get(role_select, "")
            role_prompt_text = st.session_state["role_prompt"]["prompt"]

            st.session_state["model_name"] = model_name_select
            model_config = config["models"][model_name_select]

            system_prompt_disabled = model_config.get("system_prompt_disabled", False)
            system_prompt = st.text_area(
                "System Prompt",
                # value=model_config.get("default_system_prompt", ""),
                value = role_prompt_text,
                key=f"{st.session_state['widget_key']}_System_Prompt",
                disabled=system_prompt_disabled,
            )
            with st.container():
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=1.0,
                    value=model_config.get("temperature", 1.0),
                    step=0.1,
                    key=f"{st.session_state['widget_key']}_Temperature",
                )
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    top_p = st.slider(
                        "Top-P",
                        min_value=0.0,
                        max_value=1.0,
                        value=model_config.get("top_p", 1.0),
                        step=0.01,
                        key=f"{st.session_state['widget_key']}_Top-P",
                    )
                with col2:
                    top_k = st.slider(
                        "Top-K",
                        min_value=1,
                        max_value=model_config.get("max_top_k", 500),
                        value=model_config.get("top_k", 500),
                        step=5,
                        key=f"{st.session_state['widget_key']}_Top-K",
                    )
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    max_tokens = st.slider(
                        "Max Token",
                        min_value=0,
                        max_value=4096,
                        value=model_config.get("max_tokens", 4096),
                        step=8,
                        key=f"{st.session_state['widget_key']}_Max_Token",
                    )
                with col2:
                    memory_window = st.slider(
                        "Memory Window",
                        min_value=0,
                        max_value=10,
                        value=model_config.get("memory_window", 10),
                        step=1,
                        key=f"{st.session_state['widget_key']}_Memory_Window",
                    )

    model_kwargs = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_tokens": max_tokens,
    }
    if not model_config.get("system_prompt_disabled", False):
        model_kwargs["system"] = system_prompt

    return model_kwargs, memory_window

def new_chat() -> None:
    """
    Reset the chat session and initialize a new conversation chain.
    """
    st.session_state["messages"] = [INIT_MESSAGE]
    st.session_state["langchain_messages"] = []
    st.session_state["file_uploader_key"] = random.randint(1, 100)

def display_chat_messages(
    uploaded_files: List[st.runtime.uploaded_file_manager.UploadedFile]
) -> None:
    """
    Display chat messages and uploaded images in the Streamlit app.
    """
    for message in st.session_state.messages:
        print("[DEBUG] st.session_state.message", message)
        with st.chat_message(message["role"]):
            if uploaded_files and "images" in message and message["images"]:
                display_images(message["images"], uploaded_files)

            if message["role"] == "user":
                display_user_message(message["content"])

            if message["role"] == "assistant":
                display_assistant_message(message["content"])

def display_images(
    image_ids: List[str],
    uploaded_files: List[st.runtime.uploaded_file_manager.UploadedFile],
) -> None:
    """
    Display uploaded images in the chat message.
    """
    num_cols = 10
    cols = st.columns(num_cols)
    i = 0

    for image_id in image_ids:
        for uploaded_file in uploaded_files:
            if image_id == uploaded_file.file_id:
                if uploaded_file.type.startswith('image/'):
                    img = Image.open(uploaded_file)

                    with cols[i]:
                        st.image(img, caption="", width=75)
                        i += 1

                    if i >= num_cols:
                        i = 0
                elif uploaded_file.type in ['text/plain', 'text/csv', 'text/x-python-script']:
                    if uploaded_file.type == 'text/x-python-script':
                        st.write(f"🐍 Uploaded Python file: {uploaded_file.name}")
                    else:
                        st.write(f"📄 Uploaded text file: {uploaded_file.name}")
                elif uploaded_file.type == 'application/pdf':
                    st.write(f"📑 Uploaded PDF file: {uploaded_file.name}")

def display_user_message(message_content: Union[str, List[dict]]) -> None:
    """
    Display user message in the chat message.
    """
    if isinstance(message_content, str):
        message_text = message_content
    elif isinstance(message_content, dict):
        message_text = message_content["input"][0]["content"][0]["text"]
    else:
        message_text = message_content[0]["text"]

    message_content_markdown = message_text.split('</context>\n\n', 1)[-1] if message_text is not None else ""
    st.markdown(message_content_markdown)


def display_assistant_message(message_content: Union[str, dict]) -> None:
    """
    Display assistant message in the chat message.
    """
    if isinstance(message_content, str):
        st.markdown(message_content)
    elif "response" in message_content:
        st.markdown(message_content["response"])


def langchain_messages_format(
    messages: List[Union["AIMessage", "HumanMessage"]]
) -> List[Union["AIMessage", "HumanMessage"]]:
    """
    Format the messages for the LangChain conversation chain.
    """
    from langchain_core.messages import AIMessage, HumanMessage

    for i, message in enumerate(messages):
        if isinstance(message.content, list):
            if "role" in message.content[0]:
                if message.type == "ai":
                    message = AIMessage(message.content[0]["content"])
                if message.type == "human":
                    message = HumanMessage(message.content[0]["content"])
                messages[i] = message
    return messages

def _handle_error(error)->str:
    return str(error)[:50]

def get_agentic_chatbot_conversation_chain(chat_model: ChatModel, verbose: bool, memory_window: int, memory: ConversationBufferWindowMemory = None) -> ConversationChain:
    if memory is None:
        memory = ConversationBufferWindowMemory(
            k=memory_window,
            ai_prefix="Assistant",
            human_prefix="Hu",
            chat_memory=StreamlitChatMessageHistory(),
            return_messages=True,
            memory_key="chat_history",
            input_key="input"
        )

    print("[DEBUG] CLAUDE_AGENT_PROMPT", CLAUDE_AGENT_PROMPT)

    agent = create_react_agent(
        llm=chat_model.llm,
        tools=LLM_AGENT_TOOLS,
        prompt=CLAUDE_AGENT_PROMPT,
        stop_sequence=["最終答案", "無法回答"],
    )

    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=LLM_AGENT_TOOLS,
        verbose=verbose,
        return_intermediate_steps=True,
        memory=memory,
        # handle_parsing_errors="Check your output and make sure it conforms!",
        handle_parsing_errors=_handle_error,
    )

    # Store LLM generated responses
    if "messages" not in st.session_state:
        st.session_state.messages = [INIT_MESSAGE]

    return agent_chain

def generate_response(
    conversation: ConversationChain, input: Union[str, List[dict]]
) -> str:
    """
    Generate a response from the conversation chain with the given input.
    """
    return conversation.invoke(
        {
            "input": input, 
            "car_model": st.session_state["car_model"], 
            "language": st.session_state["chat_lang"]
        }, 
        {
            "callbacks": [StreamHandler(st.empty())]
        }
    )

def main() -> None:
    """
    Main function to run the Streamlit app.
    """
    set_page_config()

    car_model, chat_lang = render_chat_interface()

    # Generate a unique widget key only once
    if "widget_key" not in st.session_state:
        st.session_state["widget_key"] = str(random.randint(1, 1000000))

    # Add a button to start a new chat
    with st.sidebar:
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"widget_key {st.session_state['widget_key']}")
            with col2:
                st.button("New Chat", on_click=new_chat, type="primary")

    model_kwargs, memory_window = render_sidebar()

    chat_model = ChatModel(st.session_state["model_name"], model_kwargs)
    conv_chain = get_agentic_chatbot_conversation_chain(chat_model, verbose=True, memory_window=memory_window)

    # Image uploader
    if "file_uploader_key" not in st.session_state:
        st.session_state["file_uploader_key"] = 0

    # Display chat messages
    uploaded_files = []
    display_chat_messages(uploaded_files)

    # User-provided prompt
    prompt = st.chat_input(
        "如何開啟和關閉 Gogoro 電動機車的系統電源？"
    )

    if prompt:  # 檢查 prompt 是否為 None 或空字符串
        formatted_prompt = chat_model.format_prompt(prompt)
        st.session_state.messages.append({"role": "user", "content": formatted_prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    # Modify langchain_messages format
    st.session_state["langchain_messages"] = langchain_messages_format(
        st.session_state["langchain_messages"]
    )

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response = conv_chain.invoke(
                {
                    "input": [{"role": "user", "content": formatted_prompt}], 
                    "car_model": car_model, 
                    "language": chat_lang
                }, 
                {
                    "callbacks": [StreamHandler(st.empty())]
                }
            )
            print("[DEBUG] response", response)
        message = {"role": "assistant", "content": response["output"]}
        st.session_state.messages.append(message)


if __name__ == "__main__":
    main()
