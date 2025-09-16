#!/usr/bin/env python3
import os
from crewai import Agent, Crew, Process
from openai import OpenAI
from crewai.project import CrewBase, agent, crew

# AGENT_ROLE: The role of the new agent
AGENT_ROLE = os.getenv("AGENT_ROLE", "")

# AGENT_GOAL: The goal of the new agent
AGENT_GOAL = os.getenv("AGENT_GOAL", "")

# AGENT_BACKSTORY: The backstory of the new agent
AGENT_BACKSTORY = os.getenv("AGENT_BACKSTORY", "")

# AGENT_API_KEY: The api key used for the llm client of the new agent
AGENT_API_KEY = os.getenv("AGENT_API_KEY", "")

# AGENT_BASE_URL: The base url of the llm client used by the new agent
AGENT_BASE_URL = os.getenv("AGENT_BASE_URL", "")

# AGENT_MODEL_NAME: The model name that the agent uses
AGENT_MODEL_NAME = os.getenv("AGENT_MODEL_NAME", "")

# AGENT_VERBOSE: Flag for more verbose agent logs
AGENT_VERBOSE = os.getenv("AGENT_VERBOSE", "")


@CrewBase
class AgentsCrew:
    """
    AgentsCrew handles the group of agents included
    in this deployment.

    Check more for crews here:
    https://docs.crewai.com/en/concepts/crews

    NOTE: You could add more agents to this crew.
    """

    @property
    def llm_client(self) -> "OpenAI":
        return OpenAI(
            api_key=AGENT_API_KEY,
            base_url=AGENT_BASE_URL
        )

    @agent
    def agent(self) -> "Agent":
        return Agent(
            role=AGENT_ROLE,
            goal=AGENT_GOAL,
            model=AGENT_MODEL_NAME,
            llm=self.llm_client,
            verbose=AGENT_VERBOSE,
            # NOTE: Here you can build your tools and add
            # them to the agent for context
            tools=[],
        )

    @crew
    def crew(self) -> "Crew":
        return Crew(
            agents=self.agents,
            # Process of agent is defined as sequential
            # check here to see other options:
            # https://docs.crewai.com/en/learn/sequential-process
            process=Process.sequential,
            verbose=True,
        )

def main():
    crew_instance = AgentsCrew()
    c = crew_instance.crew()
    result = c.kickoff()
    print(result)


if __name__ == "__main__":
    main()