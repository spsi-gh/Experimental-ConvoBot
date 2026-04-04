import streamlit as st
from agent import get_response, get_history

# with st.sidebar:
#     selected_model = st.selectbox("Select Model", ["gemini-2.5-flash", "gemini-2.5-pro"])
# model = genai.GenerativeModel(selected_model)


st.title("CHATBOT")

# just add the chat names and current chat to session state
# use it to find the chat history using langraph memory
if "chat_names" not in st.session_state:
    st.session_state.chat_names = ["Default Chat"]

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Default Chat"

with st.sidebar:
    st.title("My Chats")

    if st.button("+ New Chat"):
        new_name = f"Chat {len(st.session_state.chat_names) + 1}"
        st.session_state.chat_names.append(new_name)
        st.session_state.current_chat = new_name   
        st.rerun() 

    chat_selection = st.radio(
        "Select Convo",
        options=st.session_state.chat_names,
        index=st.session_state.chat_names.index(st.session_state.current_chat)
    )
    st.session_state.current_chat = chat_selection

# Fetch history
history = get_history(thread_id=st.session_state.current_chat)

for message in history:
    role = "user" if message.type == "human" else "assistant"
    with st.chat_message(role):  #display the messages along with role
        st.markdown(message.content)

if prompt := st.chat_input(
    "What's up?",
    accept_file="multiple",
    ):

    user_prompt = prompt.text
    uploaded_files = prompt.files

    if user_prompt:   
        with st.chat_message("user"):
            st.markdown(user_prompt)
    
    if uploaded_files:
        for file in uploaded_files:
            if file.type.startswith("image/"):
                st.image(file, caption=file.name)
            else:
                st.info(f"Attached files : {file.name}")

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_stream = get_response(prompt, thread_id=st.session_state.current_chat)
            try:
                response = st.write_stream(response_stream)
            except ValueError:
                st.write("Ok")

            #NO APPEND NEEDED HERE
            # if response:
            #     st.session_state.chats[st.session_state.current_chat].append({"role":"assistant", "content":response})
