# Software Template — CrewAI Crew

This Software Template can be used to create a new source code repository and a new GitOps deployment repository for a **CrewAI Crew Application**.

This application uses the [CrewAI framework](https://docs.crewai.com) to define, configure, and orchestrate multiple agents working together. Configuration is controlled via YAML files and environment variables, making it container-friendly and easy to run on Kubernetes or OpenShift.

### **Tools Configuration**

- MCP (Model Context Protocol) tool servers
- Tool name, URL, and transport protocol (streamable-http or sse)
- Optional bearer token authentication

### **Default LLM Configuration**

- Default LLM API Key Secret Name & Field
- Default LLM Base URL
- Default LLM Model Name

### **Agents Configuration**

- Multiple agents with roles, goals, and backstories
- Assign MCP tools to agents
- Optional per-agent custom LLM configuration (overrides default)

### **Tasks Configuration**

- Multiple tasks assigned to agents
- Task descriptions and expected outputs

### **Repository Information**

- GitHub repository
- Repository owner
- Name and branch for the repository

### **Deployment Information**

- Application deployment namespace
- Image registry and image name
- GitOps configuration for environment variables and secrets (e.g. API keys, model endpoint)

---

For more information, see the Template [source code repository](https://github.com/thepetk/double-zero-seven).
