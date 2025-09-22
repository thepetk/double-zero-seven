#!/usr/bin/env python3
from dataclasses import dataclass, field
import logging
import os
from typing import Any

import streamlit as st
import yaml
from openai import OpenAI
from langgraph.graph import StateGraph, START, END

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


def _load_yaml(path: "str") -> "dict[str, str]":
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _llm() -> "OpenAI":
    return OpenAI(base_url=LLM_BASE_URL or None, api_key=LLM_API_KEY or None)


@dataclass
class TeamState:
    topic: "str" = ""
    research: "str" = ""
    draft: "str" = ""
    review: "str" = ""
    result: "str" = ""
    logs: "list[str]" = field(default_factory=list)


class ResearchTeam:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self) -> "None":
        self.agents_cfg = _load_yaml(self.agents_config)
        self.tasks_cfg = _load_yaml(self.tasks_config)
        self.client = _llm()
        self.graph = self._build_graph()

    def _prompt(
        self, role_key: "str", task_key: "str", extra_user: "str"
    ) -> "list[dict[str, str]]":
        a_cfg = self.agents_cfg.get(role_key, {}) or {}
        t_cfg = self.tasks_cfg.get(task_key, {}) or {}
        role = a_cfg.get("role", role_key)
        goal = a_cfg.get("goal", "")
        backstory = a_cfg.get("backstory", "")
        desc = t_cfg.get("description", "")
        expected = t_cfg.get("expected_output", "")
        sys = f"You are a helpful {role}.\nGoal: {goal}\n{('Backstory: ' + backstory) if backstory else ''}".strip()
        usr = f"{desc}\n\n{extra_user}\n{('Expected output: ' + expected) if expected else ''}".strip()
        return [{"role": "system", "content": sys}, {"role": "user", "content": usr}]

    def _call(self, messages: "list[dict[str, str]]", temperature=0.2) -> "str":
        resp = self.client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content

    def _researcher(self, state: "TeamState") -> "TeamState":
        logging.getLogger("team").info("Researcher running")
        topic = state.topic
        msgs = self._prompt("researcher", "research_topic", f"Topic: {topic}")
        try:
            state.research = self._call(msgs)
        except Exception as e:
            state.research = f"LLM error in researcher: {e}"
            logging.getLogger("team").exception("Researcher failed")
        return state

    def _writer(self, state: "TeamState") -> "TeamState":
        logging.getLogger("team").info("Writer running")
        research = state.research
        msgs = self._prompt(
            "writer", "write_draft", f"Use this research:\n\n{research}"
        )
        try:
            state.draft = self._call(msgs)
        except Exception as e:
            state.draft = f"LLM error in writer: {e}"
            logging.getLogger("team").exception("Writer failed")
        return state

    def _reviewer(self, state: "TeamState") -> "TeamState":
        logging.getLogger("team").info("Reviewer running")
        draft = state.draft
        msgs = self._prompt(
            "reviewer", "review_draft", f"Review and improve this draft:\n\n{draft}"
        )
        try:
            state.review = self._call(msgs)
        except Exception as e:
            state.review = f"LLM error in reviewer: {e}"
            logging.getLogger("team").exception("Reviewer failed")
        return state

    def _finalizer(self, state: "TeamState") -> "TeamState":
        logging.getLogger("team").info("Finalizer running")
        topic = state.topic
        research = state.research
        draft = state.draft
        review = state.review
        msgs = self._prompt(
            "finalizer",
            "finalize_output",
            f"Topic: {topic}\n\nResearch:\n{research}\n\nDraft:\n{draft}\n\nReviewer notes:\n{review}\n\nProduce the final result.",
        )
        try:
            state.result = self._call(msgs)
        except Exception as e:
            state.result = f"LLM error in finalizer: {e}"
            logging.getLogger("team").exception("Finalizer failed")
        return state

    def _build_graph(self) -> "Any":
        sg = StateGraph(TeamState)
        sg.add_node("researcher", self._researcher)
        sg.add_node("writer", self._writer)
        sg.add_node("reviewer", self._reviewer)
        sg.add_node("finalizer", self._finalizer)
        sg.add_edge(START, "researcher")
        sg.add_edge("researcher", "writer")
        sg.add_edge("writer", "reviewer")
        sg.add_edge("reviewer", "finalizer")
        sg.add_edge("finalizer", END)
        return sg.compile()


def run_team(graph: "StateGraph", inputs: "dict[str, str]") -> "tuple[str, list[str]]":
    logs: "list[str]" = []
    handler = ListHandler(logs)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    targets = [logging.getLogger("team"), logging.getLogger()]
    for lg in targets:
        lg.setLevel(logging.INFO)
        lg.addHandler(handler)

    try:
        init: "TeamState" = {"topic": inputs.get("topic", ""), "logs": logs}
        out: "TeamState" = graph.invoke(init)
        return str(out.get("result", "")), logs
    finally:
        for lg in targets:
            lg.removeHandler(handler)


def main() -> "None":
    st.set_page_config(page_title="LangGraph Sample", page_icon="🤖", layout="wide")
    st.title("🤖 LangGraph Sample — Graph & Streamlit")

    team = ResearchTeam()
    graph = team.graph

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

    st.markdown("#### Team overview")
    a_col, t_col = st.columns(2)

    with a_col:
        st.markdown("**Agents**")
        for key, a in (team.agents_cfg or {}).items():
            st.markdown(f"- **{a.get('role', key)}** — goal: _{a.get('goal', '')}_")

    with t_col:
        st.markdown("**Tasks**")
        for key, t in (team.tasks_cfg or {}).items():
            desc = (t.get("description", "") or "")[:50]
            st.markdown(f"- **{desc}...**")

    st.markdown("#### Run the team")
    topic = st.text_input("Topic", value="CrewAI vs LangGraph")
    run_btn = st.button("🚀 Kick off")

    if run_btn:
        with st.spinner("Running crew..."):
            try:
                result, logs = run_team(graph, inputs={"topic": topic})
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
