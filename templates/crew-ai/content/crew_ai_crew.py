#!/usr/bin/env python3
import logging
import os

import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task

# LLM_API_KEY: Is the api key for the llm service
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

# LLM_BASE_URL: Is the base url of the llm service
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")

# LLM_MODEL_NAME: Is the base url of the llm service
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "")


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

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def get_llm_client(self) -> "LLM":
        return LLM(
            base_url=LLM_BASE_URL, api_key=LLM_API_KEY, model=f"openai/{LLM_MODEL_NAME}"
        )

    @agent
    def researcher(self) -> "Agent":
        return Agent(
            config=self.agents_config["researcher"],
            verbose=True,
            llm=self.get_llm_client(),
            tools=[],
        )

    @task
    def summarize_topic(self) -> "Task":
        return Task(
            config=self.tasks_config["summarize_topic"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


def run_crew(crew: "Crew", inputs: "dict[str, str]") -> "tuple[str, list[str]]":
    logs: list[str] = []
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
