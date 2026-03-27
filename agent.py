# agent.py

from langchain.agents import initialize_agent
from langchain.tools import Tool
from backend.tools import route_planner, ticket_suggestions, hotel_recommendations
from backend.memory import memory
from prompts.prompts import ITINERARY_PROMPT
from langchain_groq import ChatGroq
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# ---------------- GROQ API KEY ----------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ GROQ_API_KEY is missing. Check your .env file")

# ---------------- LLM SETUP ----------------
llm = ChatGroq(
    groq_api_key=api_key,
    model_name="llama-3.1-8b-instant",  # LLaMA 2–13B with 2k token context
    temperature=0.7
)

# ---------------- TOOLS ----------------
tools = [
    Tool(
        name="Route Planner",
        func=route_planner,
        description="Provides route info between source and destination cities"
    ),
    Tool(
        name="Ticket Suggestions",
        func=ticket_suggestions,
        description="Suggests ticket details based on transportation mode"
    ),
    Tool(
        name="Hotel Recommendations",
        func=hotel_recommendations,
        description="Returns hotels under given budget"
    )
]

# ---------------- AGENT ----------------
agent = initialize_agent(
    tools,
    llm,
    agent="conversational-react-description",
    memory=memory,
    verbose=True
)

# ---------------- HELPER FUNCTIONS ----------------
# Async wrapper for agent.run (non-blocking)
async def run_agent_async(query: str) -> str:
    """
    Run LangChain agent in a separate thread to avoid blocking FastAPI event loop.
    """
    try:
        return await asyncio.to_thread(lambda: str(agent.invoke({"input": query})["output"]))
    except Exception as e:
        return f"❌ Agent error: {str(e)}"

    
    