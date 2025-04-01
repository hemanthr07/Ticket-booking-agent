# from groqcloud.api import GroqChat  # Hypothetical import for GroqCloud
from groq import Groq
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langgraph.graph import Graph

import os

# Set environment variables for APIs
groqcloud_api_key = 'KEY'
os.environ['GROQCLOUD_API_KEY'] = groqcloud_api_key
os.environ["OPENWEATHERMAP_API_KEY"] = 'KEY'

# Initialize GroqCloud API
groq_llm = Groq(api_key=groqcloud_api_key)
weather = OpenWeatherMapAPIWrapper()

# Define agent node
def agent(input_1):
    # Use the correct method to send the input prompt to the Groq API
    res = groq_llm.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are given one question and you have to extract city name from it. "
                           "Don't respond anything except the city name and don't reply anything if you can't find a city name."
            },
            {
                "role": "user",
                "content": input_1,
            }
        ],
        model="llama3-8b-8192"  # Specify the model you want to use
    )
    # Extract and return the response content
    return res.choices[0].message.content

# Node to find weather information
def weather_tool(input_2):
    data = weather.run(input_2)
    return data

# Create workflow
workflow = Graph()

workflow.add_node("agent", agent)
workflow.add_node("weather", weather_tool)

# Connecting 2 nodes
workflow.add_edge('agent', 'weather')

workflow.set_entry_point("agent")
workflow.set_finish_point("weather")

app = workflow.compile()

# Invoke workflow
result = app.invoke("Capital of Texas?")
print(result)
