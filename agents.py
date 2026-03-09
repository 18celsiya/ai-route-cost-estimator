# ================================================
# Route Cost Calculator AI - Agents (Memory Enabled)
# ================================================
from dotenv import load_dotenv
import os
from crewai import Agent
from crewai.memory import Memory
from tools import get_city_distance
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Groq LLM client
llm = ChatGroq(
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="groq/openai/gpt-oss-20b"
)

# -----------------------------
# Agents
# -----------------------------

single_trip_agent = Agent(
    role="Trip Distance & Cost Bot",
    goal="Calculate travel distance and cost",
    backstory="Quickly collect start, destination, mode, unit, and country. Use tools to find distance.",
    llm=llm,
    tools=[get_city_distance],
    memory=Memory(),  # ENABLE memory
    allow_delegation=False
)

distance_calculator = Agent(
    role="Distance Calculator",
    goal="Convert meters to km or miles",
    backstory="Convert distance from meters to km or miles, round to 2 decimals, return only the number with unit, e.g., '1349.32 km'.",
    llm=llm,
    tools=[get_city_distance],
    temperature=0,
    verbose=True,
    max_execution_time=1200,
    memory=False,
    allow_delegation=False
)

travel_agent = Agent(
    role="Travel Cost Calculator",
    goal="Calculate travel cost from distance",
    backstory="Multiply numeric distance by cost rate. Add currency symbol based on country. Return only the cost with symbol, e.g., '₹2400'.",
    llm=llm,
    temperature=0,
    verbose=True,
    memory=False,
    max_execution_time=1200,
    allow_delegation=False
)

print("✅ Agents created successfully with memory enabled.")