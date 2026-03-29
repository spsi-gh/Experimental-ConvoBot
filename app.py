import streamlit as st
import google.generativeai as genai
import time
from dotenv import load_dotenv
import os

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

if "messages" not in st.session_state: #create a new session message window if not created
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):  #display the messages along with role
        st.markdown(message["content"])

if prompt := st.chat_input("What's up?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role":"user", "content":prompt}) #add the message in history

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_stream = model.generate_content(prompt, stream=True)
            response = st.write_stream(clean_steam(response_stream))
            if response:
                st.session_state.messages.append({"role":"assistant", "content":response})
