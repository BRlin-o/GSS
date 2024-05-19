import base64
import random
from io import BytesIO
import os
from typing import List, Tuple, Union, Dict

import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools.render import render_text_description
from langchain.prompts.prompt import PromptTemplate
from langchain.callbacks.manager import CallbackManager

from PIL import Image, UnidentifiedImageError

from config import config
from models import ChatModel
from prompts import CLAUDE_AGENT_PROMPT
from tools import LLM_AGENT_TOOLS
from uis import INIT_MESSAGE, set_page_config, render_chat_interface, render_sidebar

from dotenv import load_dotenv
load_dotenv()

class StreamHandler(BaseCallbackHandler):
    """
    Callback handler to stream the generated text to Streamlit.
    Callback handler 用於將生成的文本流式傳輸到 Streamlit。
    """

    def __init__(self, container: st.container, initial_text: str="") -> None:
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        Append the new token to the text and update the Streamlit container.
        將新令牌附加到文本並更新 Streamlit 容器。
        """
        self.text += token
        self.container.markdown(self.text, unsafe_allow_html=True)

def display_chat_messages(
    uploaded_files: List[st.runtime.uploaded_file_manager.UploadedFile]
) -> None:
    """
    Display chat messages and uploaded images in the Streamlit app.
    顯示聊天消息和上傳的圖片。
    """
    for message in st.session_state.messages:
        # print("[DEBUG] st.session_state.message", message)
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
    在聊天消息中顯示上傳的圖片。
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
    顯示用戶消息。
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
    顯示助理消息。
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
    格式化 LangChain 對話鏈的消息。
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

def get_agentic_chatbot_conversation_chain(chat_model: ChatModel, verbose: bool, memory: ConversationBufferWindowMemory, prompt=None):
    """
    獲取 agent chain。
    """
    _prompt = CLAUDE_AGENT_PROMPT if prompt is None else PromptTemplate.from_template(
        template=prompt
    )
    print("[DEBUG] prompt", _prompt)

    agent = create_react_agent(
        llm=chat_model.llm,
        tools=LLM_AGENT_TOOLS,
        prompt=_prompt,
        stop_sequence=["End of response."],
    )

    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=LLM_AGENT_TOOLS,
        verbose=verbose,
        return_intermediate_steps=False,
        memory=memory,
        # handle_parsing_errors="Check your output and make sure it conforms!",
        handle_parsing_errors=True,
    )

    # Store LLM generated responses
    # 存儲 LLM 生成的response
    if "messages" not in st.session_state:
        st.session_state.messages = [INIT_MESSAGE]

    return agent_chain

def main() -> None:
    """
    Main function to run the Streamlit app.
    主函數運行 Streamlit 應用程序。
    """
    set_page_config()

    car_model, chat_lang = render_chat_interface()
    global CAR_MODEL
    CAR_MODEL = car_model

    # Generate a unique widget key only once
    # 生成唯一的 widget 鍵
    if "widget_key" not in st.session_state:
        st.session_state["widget_key"] = str(random.randint(1, 1000000))

    model_kwargs, memory_window = render_sidebar(config["models"], CLAUDE_AGENT_PROMPT)
    chat_model = ChatModel(
        st.session_state["model_name"], 
        model_kwargs, 
        callback_manager=CallbackManager([FinalStreamingStdOutCallbackHandler()])
    )
    memory = ConversationBufferWindowMemory(
        k=memory_window,
        ai_prefix="Assistant",
        human_prefix="Hu",
        chat_memory=StreamlitChatMessageHistory(),
        return_messages=False,
        memory_key="chat_history",
        input_key="input"
    )
    conv_chain = get_agentic_chatbot_conversation_chain(
        chat_model,
        verbose=True,
        memory=memory,
        prompt=model_kwargs["system"]
    )

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
    # 修改 langchain_messages 格式
    st.session_state["langchain_messages"] = langchain_messages_format(
        st.session_state["langchain_messages"]
    )

    # Generate a new response if last message is not from assistant
    # 如果最後一條消息不是來自助手，則生成新的響應
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
                },
                stop=["End of response."]
            )
            print("[DEBUG] response", response)
        message = {"role": "assistant", "content": response["output"]}
        st.session_state.messages.append(message)
        st.experimental_rerun()

if __name__ == "__main__":
    main()
