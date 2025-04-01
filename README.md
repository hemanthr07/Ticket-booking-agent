#✈️ AI-Powered Assistant Suite for Tweets, Weather, and Flights
This project contains a multi-functional set of AI agents powered by LangChain, Groq, and external APIs. The system supports:

Tweet drafting and reflection via LLM

Flight lookup based on user natural language queries

Weather forecasting using location extraction + OpenWeatherMap API

🔧 Project Structure
main.py – 🌤️ Weather Agent
Extracts city name from a user's weather-related question using the Groq LLM (LLaMA 3).

Fetches current weather via OpenWeatherMap.

Built using LangGraph to define a two-node workflow:

Node 1: agent (City extractor)

Node 2: weather_tool (API call and response)

flight_booking_agent.py – 🛫 Flight Finder Agent
Parses natural queries like "Find flights from Delhi to New York".

Uses Groq LLM to extract source/destination cities and resolve IATA airport codes.

Queries AviationStack API to get real-time flight data.

Returns clean, readable flight options with departure/arrival times.

Workflow defined using 4 chained nodes:

extract_cities

airport_lookup

flight_search

respond

chains.py – 🐦 Tweet Generation and Review
Uses LangChain Prompt Templates to:

Generate viral tweets based on input.

Reflect and critique user-submitted tweets with suggestions.

Chains:

generate_chain – Generates tweet drafts.

reflect_chain – Evaluates and recommends improvements.
