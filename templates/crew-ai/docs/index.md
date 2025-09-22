# Software Template — CrewAI Agent

This Software Template can be used to create a new source code repository and a new GitOps deployment repository for a **CrewAI Agent Application**.

This application uses the [CrewAI framework](https://docs.crewai.com) to define, configure, and orchestrate agents. Configuration is controlled entirely via environment variables, which makes it container-friendly and easy to run on Kubernetes or OpenShift.

### **Application Information**

- Application name
- LLM API Key Secret Name & Field
- LLM Base URL
- LLM Model Name

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
