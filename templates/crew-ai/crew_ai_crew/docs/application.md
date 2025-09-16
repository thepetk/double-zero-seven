# CrewAI Example Agent Application

## Application Information

The application created by this Software Template provisions a **CrewAI agent** that can connect to an existing LLM backend (such as [Llama-Stack](https://github.com/meta-llama/llama-stack) or any other OpenAI-compatible service).

This application uses the [CrewAI framework](https://docs.crewai.com) to define, configure, and orchestrate agents. Configuration is controlled entirely via environment variables, which makes it container-friendly and easy to run on Kubernetes or OpenShift.

At runtime, the application:

- Instantiates an `Agent` with a role, goal, backstory, and model.
- Configures the agent's LLM client (`OpenAI` compatible) using the provided API key and base URL.
- Creates a `Crew` containing the agent.
- Runs the crew sequentially with `kickoff()` and prints the result.

## Configuration

The following environment variables are used to configure the agent:

| Variable           | Description                                                            |
| ------------------ | ---------------------------------------------------------------------- |
| `AGENT_ROLE`       | The role of the agent (e.g. `"Research Analyst"`)                      |
| `AGENT_GOAL`       | The goal of the agent (e.g. `"Summarize topics for stakeholders"`)     |
| `AGENT_BACKSTORY`  | Optional backstory/context for the agent                               |
| `AGENT_API_KEY`    | API key for the LLM backend (e.g. Llama-Stack or OpenAI)               |
| `AGENT_BASE_URL`   | Base URL of the LLM backend (e.g. `https://llamastack.example.com/v1`) |
| `AGENT_MODEL_NAME` | Model identifier to use (e.g. `"llama3.1:70b-instruct"`)               |
| `AGENT_VERBOSE`    | Enable verbose agent logs (`true` / `false`)                           |
