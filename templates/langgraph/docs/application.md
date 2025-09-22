# LangGraph Example Agentic AI Application

## Application Information

The application created by this Software Template provisions a **LangGraph Agentic AI Application** that can connect to an existing LLM backend or any other OpenAI-compatible service.

This application uses the [LangGraph framework](https://www.langchain.com/langgraph) to define, configure, and orchestrate agents. Configuration is controlled entirely via environment variables, which makes it container-friendly and easy to run on Kubernetes or OpenShift.

At runtime, the application:

- Instantiates an `Agent` with a role, goal, backstory, and model.
- Configures the agent's LLM client (`OpenAI` compatible) using the provided API key and base URL.
- Creates a `ResearchTeam` containing the team agents.
- Runs the crew sequentially with `run_team()` and prints the result.

## Configuration

The following environment variables are used to configure the agent:

| Variable         | Description                              |
| ---------------- | ---------------------------------------- |
| `LLM_BASE_URL`   | The model service base URL               |
| `LLM_MODEL_NAME` | The model name used by the model service |

**NOTE**: You have to create a secret with the API key of your model service inside and provide it to the template creation form.
