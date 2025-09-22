# CrewAI Example Crew Application

## Application Information

The application created by this Software Template provisions a **CrewAI Crw** that can connect to an existing LLM backend or any other OpenAI-compatible service.

This application uses the [CrewAI framework](https://docs.crewai.com) to define, configure, and orchestrate agents. Configuration is controlled entirely via environment variables, which makes it container-friendly and easy to run on Kubernetes or OpenShift.

At runtime, the application:

- Instantiates an `Agent` with a role, goal, backstory, and model.
- Configures the agent's LLM client (`OpenAI` compatible) using the provided API key and base URL.
- Creates a `Crew` containing the agent.
- Runs the crew sequentially with `kickoff()` and prints the result.

## Configuration

The following environment variables are used to configure the agent:

| Variable         | Description                              |
| ---------------- | ---------------------------------------- |
| `LLM_BASE_URL`   | The model service base URL               |
| `LLM_MODEL_NAME` | The model name used by the model service |

**NOTE**: You have to create a secret with the API key of your model service inside and provide it to the template creation form.
