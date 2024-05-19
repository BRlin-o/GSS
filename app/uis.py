import random
import streamlit as st
from typing import List, Tuple, Union, Dict

INIT_MESSAGE = {
    "role": "assistant",
    "content": "尊貴的車主您好，我是您專屬的Gogoro Smart Scooter萬事通，很高興為您解答任何關於Gogoro的問題。",
}

def set_page_config() -> None:
    """
    Set the Streamlit page configuration.
    設置 Streamlit 頁面配置。
    """
    st.set_page_config(page_title="Chat with GSS", page_icon="🏍️", layout="wide")

def set_CAR_MODEL_From_Session():
    global CAR_MODEL
    CAR_MODEL = st.session_state["car_model"]
    print("[DEBUG] set_CAR_MODEL_From_Session", CAR_MODEL)

def render_chat_interface():
    """
    渲染聊天界面。
    """
    st.title("🏍️ Gogoro Smart Scooter 萬事通")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            car_model = st.selectbox(
                "車型", 
                ["CrossOver", "Delight", "JEGO", "SuperSport", "VIVA MIX", "VIVA XL", "VIVA", "S1", "S2", "S3"],
                on_change=set_CAR_MODEL_From_Session
            )
            st.session_state["car_model"] = car_model
        with col2:
            chat_lang = st.selectbox("語言", ["繁體中文", "English"])
            st.session_state["chat_lang"] = chat_lang
    return car_model, chat_lang

def new_chat(init_message=INIT_MESSAGE) -> None:
    """
    Reset the chat session and initialize a new conversation chain.
    重置聊天會話並初始化新的對話鏈。
    """
    st.session_state["messages"] = [init_message]
    st.session_state["langchain_messages"] = []
    st.session_state["file_uploader_key"] = random.randint(1, 100)

def render_sidebar(model_list, default_prompt) -> Tuple[Dict, int, str]:
    """
    Render the sidebar UI and return the inference parameters.
    渲染側邊欄 UI 並返回推理參數。
    """
    # Add a button to start a new chat
    with st.sidebar:
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"widget_key {st.session_state['widget_key']}")
            with col2:
                st.button("New Chat", on_click=new_chat, type="primary")
    with st.sidebar:
        with st.expander("LLM Settings"):
            model_name_select = st.selectbox(
                'Model',
                list(model_list.keys()),
                key=f"{st.session_state['widget_key']}_Model_Id",
            )
            st.session_state["model_name"] = model_name_select
            model_config = model_list[model_name_select]

            # Set the initial value of the text area based on the selected role
            # 根據選定的角色設置文本區域的初始值
            st.session_state["role_prompt"] = default_prompt

            system_prompt_disabled = model_config.get("system_prompt_disabled", False)
            system_prompt = st.text_area(
                "System Prompt",
                value = st.session_state["role_prompt"].template,
                key=f"{st.session_state['widget_key']}_System_Prompt",
                disabled=system_prompt_disabled,
            )
            with st.container():
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=1.0,
                    # value=model_config.get("temperature", .0),
                    value=.0,
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
