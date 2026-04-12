# agent.py

from langchain.agents import initialize_agent
from langchain.tools import Tool
from tools.flight_tools import get_flights
from tools.hotel_tools import get_hotels
from tools.bus_tools import get_buses
from tools.train_tools import get_trains
from tools.routes_tools import get_route
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
# ---------------- TOOL WRAPPERS ----------------
def flights_tool(input_str):
    try:
        origin, destination = input_str.split(",")
        return get_flights(origin.strip(), destination.strip())
    except:
        return "Invalid input. Use format: Karachi, Lahore"

def hotels_tool(city):
    return get_hotels(city)

def buses_tool(input_str):
    origin, destination = input_str.split(",")
    return get_buses(origin.strip(), destination.strip())

def trains_tool(input_str):
    origin, destination = input_str.split(",")
    return get_trains(origin.strip(), destination.strip())

def route_tool(input_str):
    origin, destination = input_str.split(",")
    return get_route(origin.strip(), destination.strip())
# ---------------- TOOLS ----------------
tools = [
    Tool(name="Flights", func=flights_tool, description="Input: 'Karachi, Lahore'"),
    Tool(name="Hotels", func=hotels_tool, description="Input: city name"),
    Tool(name="Buses", func=buses_tool, description="Input: 'Karachi, Lahore'"),
    Tool(name="Trains", func=trains_tool, description="Input: 'Karachi, Lahore'"),
    Tool(name="Route Info", func=route_tool, description="Input: 'Karachi, Lahore'")
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

    
    