import streamlit as st
import openai
import os
from dotenv import load_dotenv
import random
import time
from langchain.chat_models import ChatOpenAI



# load_dotenv()

openai_api_key = st.sidebar.text_input('OpenAI API Key')

MAJOR_QUESTIONS = [
    "Have you noticed any changes in your thoughts, feelings, or behaviors that are causing you distress or difficulty in functioning?",
    "How long have you been experiencing these symptoms?",
    "Have you noticed any patterns or triggers related to your symptoms?",
    "Do these feelings or behaviors happen across different situations and settings (like at work, home, school)?",
    "Have you experienced any thoughts of death or suicide, or made any plans or attempts? ",
]
st.session_state.question_list = MAJOR_QUESTIONS.copy()
st.title("MEDinfinite Dignostic Tool")

if not openai_api_key.startswith('sk-'):
    st.warning('Please enter your OpenAI API key!', icon='⚠')
    # st.secrets["OPENAI_API_KEY"] = openai_api_key
    # Set OpenAI API key from Streamlit secrets
else:
    openai.api_key = openai_api_key
    st.session_state.llm = ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo', verbose=True, openai_api_key=openai_api_key)

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

def reset_session():
    st.session_state.messages = []
    st.session_state.content = []
    st.session_state.init_question = st.session_state.question_list

st.button("Reset", on_click=reset_session)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.content = []
    st.session_state.init_question = MAJOR_QUESTIONS.copy()

if (st.session_state.messages == []) & (len(st.session_state.init_question) == len(MAJOR_QUESTIONS)):
    message = st.chat_message("assistant")
    q1 = st.session_state.init_question.pop(0)
    full_prompt = "You will be asked 5 questions. Please answer them as completely as possible. '\n' " + q1
    message.write(full_prompt)
    i = 0
    st.session_state.messages.append({"role": "assistant", "content": full_prompt})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input

if prompt := st.chat_input():

    # Add user message to chat history
    i = len(MAJOR_QUESTIONS)-(len(st.session_state.init_question)+1)
    st.session_state.content.append(f"question: {MAJOR_QUESTIONS[i]} '\n' patinet:  {prompt}")
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    if st.session_state.init_question:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            q1 = st.session_state.init_question.pop(0)
            full_prompt = f"next question: {q1}"
            st.session_state.messages.append({"role": "assistant", "content": full_prompt})
            message_placeholder.markdown(full_prompt + "▌")
        # Add assistant response to chat history
        # st.session_state.messages.append({"role": "assistant", "content": full_prompt})

if len(st.session_state.content) == len(MAJOR_QUESTIONS):
    message = st.chat_message("assistant")
    message.write("diagnostic in progress ......")
    dialog_str = "'\n''\n'".join(st.session_state.content)
    prompt = f""" Assume you are a psychologist. 5 questions and answers will be presented to you. Provide your best 
    educated guess on the patient's diagnostics. You should consider DSM-5 in every step of the process. After diagnostics, 
    explain what made you make that diagnostic. Below is the Q&A:
    
    {dialog_str}
    """
    response = st.session_state.llm.predict(prompt)
    message = st.chat_message("assistant")
    message.write(response)
