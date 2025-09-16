# Software Template — CrewAI Agent

This Software Template can be used to create a new source code repository and a new GitOps deployment repository for a **CrewAI Agent Application**.

The generated application provisions a containerized **CrewAI agent** that connects to an existing LLM backend (for example, [Llama-Stack](https://github.com/meta-llama/llama-stack) or any other OpenAI-compatible service).  
It uses the [CrewAI framework](https://docs.crewai.com) to define the agent role, goal, backstory, and tasks.  
Configuration is controlled entirely through environment variables, making the application portable and easy to deploy on Kubernetes or OpenShift.

---

### **Application Information**

- Application name
- Agent role, goal, and backstory
- Model backend of choice (Llama-Stack or other OpenAI-compatible service)
- Model name to run the agent with

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
