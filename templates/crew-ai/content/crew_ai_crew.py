#!/usr/bin/env python3
__import__("pysqlite3")
import sys

sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import logging
import os

import streamlit as st
from pathlib import Path
import yaml
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, crew

# LLM_API_KEY: Is the api key for the llm service
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

# LLM_BASE_URL: Is the base url of the llm service
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")

# LLM_MODEL_NAME: Is the base url of the llm service
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "")


class ConfigPath:
    AGENTS = Path(__file__).parent / "config" / "agents.yaml"
    TASKS = Path(__file__).parent / "config" / "tasks.yaml"


class ListHandler(logging.Handler):
    """
    helper class to capture the logs from crewAI
    """

    def __init__(self, buf: "list[str]") -> "None":
        super().__init__()
        self.buf = buf

    def emit(self, record: "logging.LogRecord") -> "None":
        try:
            self.buf.append(self.format(record))
        except Exception:
            pass


@CrewBase
class ResearchCrew:
    """A simple research crew Services Crew"""

    def __init__(self) -> "None":
        super().__init__()
        with ConfigPath.AGENTS.open("r", encoding="utf-8") as f:
            self.agents_config: "dict[str, dict[str, str]]" = yaml.safe_load(f) or {}
        with ConfigPath.TASKS.open("r", encoding="utf-8") as f:
            self.tasks_config: "dict[str, dict[str, str]]" = yaml.safe_load(f) or {}

        self._agents_dict: "dict[str, Agent]" = {}

    def get_llm_client(self) -> "LLM":
        return LLM(
            base_url=LLM_BASE_URL, api_key=LLM_API_KEY, model=f"openai/{LLM_MODEL_NAME}"
        )

    def _build_agents(self) -> "list[Agent]":
        """
        builds a list of agents based on the configuration
        """
        llm = self.get_llm_client()
        agents: "list[Agent]" = []
        self._agents_dict: "dict[str, Agent]" = {}

        for name, cfg in self.agents_config.items():
            agent_kwargs = dict(config=cfg, llm=llm, tools=[])
            agent = Agent(**agent_kwargs)
            agents.append(agent)
            self._agents_dict[name] = agent

        return agents

    def _build_tasks(self) -> "list[Task]":
        tasks: "list[Task]" = []

        for name, cfg in self.tasks_config.items():
            agent_name = cfg.get("agent")
            if not agent_name or agent_name not in self._agents_dict:
                raise ValueError(
                    f"Task '{name}' references unknown agent '{agent_name}'"
                )

            task = Task(config=cfg, agent=self._agents_dict[agent_name])
            tasks.append(task)
        return tasks

    @crew
    def crew(self) -> "Crew":
        """Creates the Research Crew"""
        agents = self._build_agents()
        tasks = self._build_tasks()
        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )


def run_crew(crew: "Crew", inputs: "dict[str, str]") -> "tuple[str, list[str]]":
    logs: "list[str]" = []
    handler = ListHandler(logs)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    targets = [logging.getLogger("crewai"), logging.getLogger()]

    for lg in targets:
        lg.setLevel(logging.INFO)
        lg.addHandler(handler)

    try:
        result = crew.kickoff(inputs=inputs)
        return str(result), logs
    finally:
        for lg in targets:
            lg.removeHandler(handler)


def main() -> "None":
    st.set_page_config(page_title="CrewAI Sample", page_icon="🤖", layout="wide")
    st.title("🤖 CrewAI Sample — Crews & Streamlit")

    research_crew = ResearchCrew()
    crew_obj = research_crew.crew()

    with st.sidebar:
        st.markdown("### LLM Backend")
        st.text_input(
            "LLM_BASE_URL",
            value=LLM_BASE_URL,
            disabled=True,
            help="Set via env var LLM_BASE_URL",
        )
        st.text_input(
            "LLM_API_KEY",
            value=("set" if LLM_API_KEY else "not set"),
            disabled=True,
            help="Set via env var LLM_API_KEY",
        )
        st.toggle("Verbose logs", value=True, disabled=True)

    st.markdown("#### Crew overview")

    a_col, t_col = st.columns(2)
    with a_col:
        st.markdown("**Agents**")
        for agent in crew_obj.agents:
            st.markdown(f"- **{agent.role}** — goal: _{agent.goal}_")

    with t_col:
        st.markdown("**Tasks**")
        for task in crew_obj.tasks:
            st.markdown(f"- **{getattr(task, 'description', '')[:50]}...**")

    st.markdown("#### Run the crew")
    topic = st.text_input("Topic", value="CrewAI vs LangGraph")
    run_btn = st.button("🚀 Kick off")

    if run_btn:
        with st.spinner("Running crew..."):
            try:
                result, logs = run_crew(crew_obj, inputs={"topic": topic})
                st.subheader("Result")
                st.write(result)
                st.subheader("Logs")
                if logs:
                    st.code("\n".join(logs), language="text")
                else:
                    st.info("No logs captured.")

                st.success("Crew completed.")
            except Exception as e:
                st.error(f"Run failed: {e}")


if __name__ == "__main__":
    main()
