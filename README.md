# Travel Planner Multi-Agent System

The Travel Planner is a multi-agent system built using the `deepagents` framework and `langchain`, utilizing LLMs (like Groq/Llama models) to automatically research and compile detailed, budget-conscious travel itineraries based on natural language queries.

## 🔄 Multi-Agent Workflow

The system follows a highly structured, hierarchical "Supervisor-Worker" workflow:

1. **Information Extraction**: When a user submits a query (e.g., *"Plan a 5-day family trip to Singapore in January 2026..."*), a lightweight extractor LLM parses the natural language into structured JSON data (destination, travel dates, party size, budget, preferences).
2. **Supervisor Orchestration**: A dynamic prompt is generated for the main **Supervisor Agent**. The Supervisor is strictly instructed to orchestrate the process by creating a 5-step task list (`todos.txt`).
3. **Delegation to Subagents**: The Supervisor delegates specific research tasks to specialized worker subagents.
4. **Parallel Research & File Writing**:
   - The **Weather Specialist** fetches forecasts and writes findings to `weather.txt`.
   - The **Research Specialist** looks up attractions, restaurants, and real-time costs, writing the data to `attractions.txt`, `food.txt`, and `costs.txt`.
5. **Synchronization**: The Supervisor monitors the workspace and waits until all required research files exist in the `data/temp` directory.
6. **Final Compilation**: Once the research phase is complete, the Supervisor spawns the **Itinerary Compiler** subagent. This final agent reads all the text files and synthesizes them into a beautifully formatted, budget-aware, day-by-day itinerary saved as `final_itinerary.txt`.

## 🤖 Agents & Functionalities

The application utilizes four distinct agent personas:

1. **Supervisor Agent**: The orchestrator. It creates the plan, manages the subagents, ensures the workflow is followed sequentially, and enforces the user's budget and constraints.
2. **Weather Specialist**: A focused agent that solely handles meteorology. It uses location data to pull upcoming weather forecasts and provides practical advice based on the weather.
3. **Research Specialist**: The heavy lifter for data gathering. It finds family-friendly activities, local cuisine, and looks up *real* current prices for hotels, flights, and food to prevent the LLM from hallucinating costs.
4. **Itinerary Compiler**: The synthesizer. It takes the raw, scattered research data from the other agents and formats it into a cohesive, realistic day-by-day travel plan.

## 🧰 Tools Available to Agents

The agents have access to a specific set of tools (found in `src/tools/`) to interact with the outside world and the local filesystem:

*   **`get_weather_forecast`**: Hits the OpenWeatherMap API to get up-to-date temperature and rain forecasts for the destination.
*   **`internet_search`**: Uses the Tavily API to search the web for general travel information and blogs.
*   **`search_places` / `osm_places`**: Uses OpenStreetMap's Nominatim geocoder to find exact points of interest, coordinates, and nearby locations.
*   **`research_costs`**: A specialized Tavily web search customized to find current pricing data. It strictly scopes its search to reliable aggregators like TripAdvisor, Booking.com, Kayak, and Agoda to ensure the budget is realistic.
*   **File Operations (`file_tools.py`)**: Tools like `list_files`, `read_file`, `write_file`, and `append_to_file`. These are critical because the agents communicate and pass state to one another asynchronously by reading and writing text files in the `data/temp/` directory.

## 🚀 Usage Examples

### 1. Planning a Family Vacation
```python
from src.agents.supervisor import create_travel_agent
from langchain_core.messages import HumanMessage

user_query = """Plan a 5-day family trip to Singapore in January 2026 for 2 adults and 2 kids. 
Budget: ₹200,000. We love beaches, food, and light adventure."""

# Initialize the supervisor agent
supervisor_agent = create_travel_agent(user_query)

# Run the agent
for chunk in supervisor_agent.stream({"messages": [HumanMessage(content=user_query)]}, stream_mode="values"):
    # Stream the output and track progress
    print(chunk)
```
*The agent will generate a family-friendly itinerary, ensuring that activities are suitable for children and the total cost stays within the ₹200,000 budget.*

### 2. Budget-Strict Solo Travel
```python
from src.agents.supervisor import create_travel_agent
from langchain_core.messages import HumanMessage

user_query = """I want a 3-day solo trip to Goa, India in December 2025.
My absolute maximum budget is ₹15,000. Find me cheap hostels, local street food, and free beaches."""

supervisor_agent = create_travel_agent(user_query)
# The Research Specialist will prioritize finding accurate, low-cost options to respect the strict budget.
```

### 3. Running the Main Script
You can directly run the main script to see the agent in action based on the default query.
```bash
python main.py
```
This will:
1. Clear the `data/temp` workspace.
2. Initialize the agent with the hardcoded query.
3. Stream the agent's thought process, tool calls, and subagent delegations to the console.
4. Finally, output the compiled itinerary.
