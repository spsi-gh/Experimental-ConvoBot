from google import genai
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage
import time
from langchain.tools import tool
from typing import Dict, Any
from tavily import TavilyClient
from langgraph.checkpoint.memory import InMemorySaver
import mimetypes

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=API_KEY)
client = genai.Client(api_key=API_KEY)

tavily_client = TavilyClient()

# Building a web-search tool
@tool
def web_search(query: str) -> Dict[str, Any]:
    """Search the web for information"""
    return tavily_client.search(query)

agent = create_agent(
    model=model,
    # tools=[web_search]
    checkpointer=InMemorySaver()
)
# get agent response
def get_response(prompt, thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    content = [{"type":"text", "text":prompt.text}]

    for file in prompt.files:
        mime_type = file.type or mimetypes.guess_type(file.name)[0] or "application/octet-stream"
        #multipurpose internet mail extension

        google_file = client.files.upload(file=file, 
                                          config={'mime_type':mime_type, 
                                                  'display_name': file.name})

        content.append({
            "type":"media",
            "file_uri":google_file.uri,
            "mime_type":mime_type
        })

    question = HumanMessage(content=content)

    stream = agent.stream(
        {"messages": [question]},
        config,
        stream_mode="messages"
    )

    has_output = False

    for chunk, metadata in stream:
        has_output = True
        if chunk.content:
            for word in chunk.content.split():
                yield word + " "
                time.sleep(0.05)

    if not has_output:
        yield ""

# get chat history
def get_history(thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    state = agent.get_state(config)
    return state.values.get("messages", []) # return the message list from agent's internal state