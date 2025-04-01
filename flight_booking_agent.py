import json
import requests
from datetime import datetime, timedelta
from groq import Groq
from langgraph.graph import Graph

# Load API Keys from Environment Variables
groq_api_key = "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"
aviation_api_key = "0d69cdbfc33105bb37443b997fd9dafa"


# Initialize Groq LLM
groq_llm = Groq(api_key=groq_api_key)


# Node 1: Extract source and destination cities
def extract_cities(user_query):
    """Extract source and destination cities from user query using Groq LLM."""
    try:
        res = groq_llm.chat.completions.create(
            messages=[
                {"role": "system", "content": "Extract the source and destination cities from the user's query. "
                                              "Reply STRICTLY in JSON format: "
                                              "{\"source\": \"city_name\", \"destination\": \"city_name\"}."},
                {"role": "user", "content": user_query},
            ],
            model="llama3-8b-8192"
        )
        response_text = res.choices[0].message.content.strip()
        cities_json = json.loads(response_text)
        return {"source_city": cities_json["source"], "destination_city": cities_json["destination"]}
    except Exception as e:
        raise ValueError(f"Failed to parse cities: {e}. Response was: {response_text}")


# Node 2: Fetch IATA airport code for a city
def get_airport_code(city):
    """
    Fetch IATA airport code for a city using Groq LLM.
    """
    try:
        res = groq_llm.chat.completions.create(
            messages=[
                {"role": "system", "content": "Provide the main airport IATA code for the given city. "
                                              "If you don't know, reply with 'N/A'."},
                {"role": "user", "content": f"City: {city}"}
            ],
            model="llama3-8b-8192"
        )
        iata_code = res.choices[0].message.content.strip()
        if iata_code == "N/A" or not iata_code:
            raise ValueError(f"No IATA code found for city: {city}")
        return iata_code
    except Exception as e:
        raise ValueError(f"Error fetching IATA code for {city}: {e}")


# Node 3: Airport lookup for source and destination cities
def airport_lookup(state):
    """Fetch IATA codes for source and destination cities."""
    source_city = state["source_city"]
    destination_city = state["destination_city"]
    try:
        source_airport = get_airport_code(source_city)
        destination_airport = get_airport_code(destination_city)
        return {"source_airport": source_airport, "destination_airport": destination_airport}
    except Exception as e:
        raise ValueError(f"Error during airport lookup: {e}")


# Node 4: Search flights using AviationStack API
def flight_search(state):
    """Fetch available flights for the coming weekend using AviationStack API."""
    source_airport = state["source_airport"]
    destination_airport = state["destination_airport"]

    # AviationStack API endpoint
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": aviation_api_key,  # Replace with your AviationStack API key
        "dep_iata": source_airport,      # IATA code for source
        "arr_iata": destination_airport, # IATA code for destination
        # limit": 10                       # Fetch a limited number of flights
    }

    print("AviationStack API Request:", url, params)  # Debugging API request
    
    try:
        response = requests.get(url, params=params)
        #print("AviationStack API Response:", response.status_code, response.text)  # Debug Response
        
        data = response.json()

        flight_options = []
        # Extract flight details
        for flight in data.get("data", []):
            flight_options.append({
                "airline": flight.get("airline", {}).get("name", "N/A"),
                "departure_time": flight.get("departure", {}).get("scheduled", "N/A"),
                "arrival_time": flight.get("arrival", {}).get("scheduled", "N/A"),
                "flight_number": flight.get("flight", {}).get("number", "N/A"),
            })

        
        if not flight_options:
            print("No flights found in API response.")
        return {"flights": flight_options}

    except Exception as e:
        print(f"Error fetching flights: {e}")
        return {"flights": []}



# Node 5: Format flight details
def responder(state):
    """Format the flight details into a response."""
    flights = state["flights"]
    if not flights:
        return "No flights available for the requested route and date."
    
    response = "Here are the available flight options\n"
    for idx, flight in enumerate(flights, 1):
        response += (f"{idx}. Airline: {flight['airline']}, "
                     f"Flight Number: {flight['flight_number']}, "
                     f"Departure: {flight['departure_time']}, "
                     f"Arrival: {flight['arrival_time']}\n")
    return response


# Workflow Definition
workflow = Graph()
workflow.add_node("extract_cities", extract_cities)
workflow.add_node("airport_lookup", airport_lookup)
workflow.add_node("flight_search", flight_search)
workflow.add_node("respond", responder)

# Connect Nodes
workflow.add_edge("extract_cities", "airport_lookup")
workflow.add_edge("airport_lookup", "flight_search")
workflow.add_edge("flight_search", "respond")

workflow.set_entry_point("extract_cities")
workflow.set_finish_point("respond")

# Compile and Run
if __name__ == "__main__":
    app = workflow.compile()
    user_query = "Find me flights from delhi to new york "
    try:
        result = app.invoke(user_query)
        print(result)
    except Exception as e:
        print(f"Error: {e}")