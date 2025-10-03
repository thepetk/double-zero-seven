# CrewAI Crew Application

## Application Information

The application created by this Software Template provisions a **CrewAI Crew** that can connect to an existing LLM backend or any other OpenAI-compatible service. It features a Streamlit web interface for managing and running the crew.

This application uses the [CrewAI framework](https://docs.crewai.com) to define, configure, and orchestrate multiple agents working together. Configuration is controlled via YAML files (`config/agents.yaml`, `config/tasks.yaml`, `config/tools.yaml`) and environment variables, which makes it container-friendly and easy to run on Kubernetes or OpenShift.

At runtime, the application:

- Loads agent configurations from `config/agents.yaml` with their roles, goals, backstories, and assigned tools
- Loads task configurations from `config/tasks.yaml` and assigns them to agents
- Connects to MCP (Model Context Protocol) tool servers defined in `config/tools.yaml`
- Configures each agent's LLM client (OpenAI compatible) using either the default LLM settings or per-agent custom LLM configuration
- Creates a `Crew` containing multiple agents and tasks
- Runs the crew sequentially with `kickoff()` and displays the result in a Streamlit UI

## Configuration

### Default LLM Configuration

The following environment variables are used to configure the default LLM for all agents:

| Variable         | Description                              |
| ---------------- | ---------------------------------------- |
| `LLM_BASE_URL`   | The default model service base URL       |
| `LLM_MODEL_NAME` | The default model name                   |
| `LLM_API_KEY`    | The default API key for the model service|

**NOTE**: You have to create a secret with the API key of your model service inside and provide it to the template creation form.

### Per-Agent LLM Configuration

Each agent can optionally override the default LLM configuration by specifying custom settings in `config/agents.yaml`:

- `llmAPIURL`: Custom LLM API URL for this agent
- `llmAPIKeyEnvVar`: Environment variable name containing the custom API key
- `model`: Custom model name for this agent

### MCP Tools Configuration

Tools are configured in `config/tools.yaml` with:

- `name`: Unique identifier for the tool server
- `url`: MCP server endpoint URL
- `transport`: Protocol type (streamable-http or sse)
- `bearerTokenEnvVarName`: (Optional) Environment variable containing the bearer token

Agents can be assigned tools by referencing the tool `name` in their `tools` array in `config/agents.yaml`.
