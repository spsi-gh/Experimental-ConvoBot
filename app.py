import streamlit as st
import google.generativeai as genai
import time
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

with st.sidebar:
    selected_model = st.selectbox("Select Model", ["gemini-2.5-flash", "gemini-2.5-pro"])
model = genai.GenerativeModel(selected_model)

def clean_steam(response_stream):
    for chunk in response_stream:
        if chunk.text:
            for word in chunk.text.split():
                yield word + " "
                time.sleep(0.05)

st.title("CHATBOT")

# if "messages" not in st.session_state: #create a new session message window if not created
#     st.session_state.messages = []

#adding multi-windows
if "chats" not in st.session_state:
    st.session_state.chats = {"Default Chat": []} #creating a dict of key-chatlist pair

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Default Chat"  #just a string obj with the same name as my default chat

with st.sidebar:
    st.title("My Chats")

    if st.button("+ New Chat"):
        new_name = f"Chat {len(st.session_state.chats) + 1}"
        st.session_state.chats[new_name] = []
        st.session_state.current_chat = new_name    

    chat_selection = st.radio(
        "Select Convo",
        options=list(st.session_state.chats.keys()),
        index=list(st.session_state.chats.keys()).index(st.session_state.current_chat)
    )
    st.session_state.current_chat = chat_selection

current_messages = st.session_state.chats[st.session_state.current_chat]
for message in current_messages:
    with st.chat_message(message["role"]):  #display the messages along with role
        st.markdown(message["content"])

if prompt := st.chat_input("What's up?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.chats[st.session_state.current_chat].append({"role":"user", "content":prompt}) #add the message in history

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_stream = model.generate_content(prompt, stream=True)
            response = st.write_stream(clean_steam(response_stream))
            if response:
                st.session_state.chats[st.session_state.current_chat].append({"role":"assistant", "content":response})
