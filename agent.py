import google.generativeai as genai
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

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
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
# get agent respon
def get_response(prompt, thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    question = HumanMessage(content=prompt)
    stream = agent.stream(
        {"messages": [question]},
        config,
        stream_mode="messages"
    )

    for chunk, metadata in stream:
        if chunk.content:
            for word in chunk.content.split():
                yield word + " "
                time.sleep(0.05)

# get chat history
def get_history(thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    state = agent.get_state(config)
    return state.values.get("messages", []) # return the message list from agent's internal state