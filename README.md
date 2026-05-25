# Travel Planner Multi-Agent System

The Travel Planner is a multi-agent system built using the `deepagents` framework and `langchain`, utilizing LLMs (like Google's Gemini models) to automatically research and compile detailed, budget-conscious travel itineraries based on natural language queries. It features a conversational interface with session management and structured output.

## 🔄 Current Architecture & Workflow

The system follows a highly structured, hierarchical "Supervisor-Worker" architecture:

1. **User Request & Session Management**: The user provides a travel query through a conversational CLI interface (`main.py`). The interaction is managed by `TravelPlannerSession`, allowing for follow-up questions and persistent memory across the session.
2. **Supervisor Orchestration**: The main **Supervisor Agent** analyzes the request and creates a structured 4-step plan using the `write_todos` skill.
3. **Task Delegation**: The Supervisor directly delegates specific tasks to specialized worker subagents via the `task` tool:
   - **Weather Specialist**: Receives the destination and travel month, fetching relevant weather forecasts.
   - **Research Specialist**: Receives trip details to look up real attractions, restaurants, and current prices.
4. **Context Passing**: Instead of writing to intermediate files, the subagents return their findings directly to the Supervisor as strings. The Supervisor collects these responses in its conversation history.
5. **Final Compilation**: The Supervisor passes the complete findings from the weather and research specialists directly to the **Itinerary Compiler** subagent.
6. **Structured Output**: The Compiler synthesizes the data into a final itinerary. The system extracts a structured format (`FinalItinerary`) to provide a clean, visually appealing summary in the console, including cost breakdowns and budget checks.

## 🤖 Agents & Functionalities

The application utilizes four distinct agent personas:

1. **Supervisor Agent**: The orchestrator. It manages the subagents, ensures the workflow is followed sequentially, passes context between them, and enforces the user's budget and constraints.
2. **Weather Specialist**: A focused agent that solely handles meteorology. It pulls upcoming weather forecasts and provides practical packing and travel advice.
3. **Research Specialist**: The heavy lifter for data gathering. It finds family-friendly activities, local cuisine, and looks up real current prices to prevent the LLM from hallucinating costs.
4. **Itinerary Compiler**: The synthesizer. It takes the raw research data and formats it into a cohesive, realistic day-by-day travel plan.

## 🚀 How to Run the Project

### Prerequisites

To run this project, you will need to sign up for several API keys. Create a `.env` file in the root directory (you can copy `.env.example` as a template) and add the following keys:

1. **Google API Key (Gemini)**:
   - Used for the LLM models driving the agents.
   - Get it here: [Google AI Studio](https://aistudio.google.com/)
2. **Tavily API Key**:
   - Used by the Research Specialist for general web search and finding current pricing.
   - Get it here: [Tavily](https://tavily.com/)
3. **SerpAPI Key**:
   - Used for Google Search integrations to look up specific places or flights.
   - Get it here: [SerpAPI](https://serpapi.com/)
4. **OpenWeather API Key**:
   - Used by the Weather Specialist to fetch real-time and historical weather data.
   - Get it here: [OpenWeather](https://openweathermap.org/api)
5. **LangSmith API Key (Optional)**:
   - Useful for tracing, debugging, and monitoring the agents' thought processes.
   - Get it here: [LangSmith](https://smith.langchain.com/)
   - To enable tracing, set `LANGCHAIN_TRACING_V2=true` in your `.env`.

### Installation

1. Clone the repository and navigate to the project directory.
2. Create and activate a Python virtual environment (recommended).
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

Run the main chat interface:
```bash
python main.py
```

- Type your travel query to begin (e.g., *"Plan a 5-day family trip to Singapore in January 2026 for 2 adults and 2 kids. Budget: ₹200,000."*).
- After the first itinerary is generated, you can ask follow-up questions freely to modify the plan.
- To start a new session, type `new session`.
- To resume a previous session, run: `python main.py --session=<session_id>`.
- Type `quit` or `exit` to close the application.
