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
from crewai.tools import BaseTool
from crewai_tools import MCPServerAdapter

# LLM_API_KEY: Is the api key for the llm service
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

# LLM_BASE_URL: Is the base url of the llm service
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")

# LLM_MODEL_NAME: Is the base url of the llm service
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "")


class ConfigPath:
    AGENTS = Path(__file__).parent / "config" / "agents.yaml"
    TASKS = Path(__file__).parent / "config" / "tasks.yaml"
    TOOLS = Path(__file__).parent / "config" / "tools.yaml"


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


class ResearchCrew:
    """A simple research crew Services Crew"""

    def __init__(self):
        with ConfigPath.AGENTS.open("r", encoding="utf-8") as f:
            self.agents_config: "dict[str, dict[str, str]]" = yaml.safe_load(f) or {}
        with ConfigPath.TASKS.open("r", encoding="utf-8") as f:
            self.tasks_config: "dict[str, dict[str, str]]" = yaml.safe_load(f) or {}
        with ConfigPath.TOOLS.open("r", encoding="utf-8") as f:
            self.tools_config: "dict[str, list[dict[str, str]]]" = (
                yaml.safe_load(f) or {}
            )

    def get_llm_client(
        self, base_url=LLM_BASE_URL, api_key=LLM_API_KEY, model=LLM_MODEL_NAME
    ) -> "LLM":
        return LLM(base_url=base_url, api_key=api_key, model=model)

    def _build_tools(self, timeout=10) -> "dict[str, BaseTool]":
        server_params_list: "list[dict[str, str]]" = []
        self._tools_dict: "dict[str, BaseTool]" = {}
        self._tool_sources: "dict[str, list[str]]" = {}
        self._disconnected_tools: "dict[str, str]" = {}
        self._mcp_adapters: "list[MCPServerAdapter]" = []

        for tc in self.tools_config["tools"]:

            # skip tools without a name
            if not tc.get("name"):
                continue

            tool_name = tc.get("name")
            transport = tc.get("transport")
            url = tc.get("url")
            params: "dict[str, str]" = {"url": url, "transport": transport}

            # check if authorization header should be added
            if tc.get("bearerTokenEnvVarName"):
                bearer = os.getenv(tc["bearerTokenEnvVarName"])
                if bearer:
                    params.setdefault("headers", {})[
                        "Authorization"
                    ] = f"Bearer {bearer}"

            server_params_list.append((tool_name, params))

        tools_by_name: "dict[str, BaseTool]" = {}

        if len(server_params_list) == 0:
            return tools_by_name

        for tool_name, params in server_params_list:
            try:
                mcp_adapter = MCPServerAdapter(params, connect_timeout=timeout)
                mcp_tools = mcp_adapter.__enter__()
                self._mcp_adapters.append(mcp_adapter)
                self._tool_sources[tool_name] = []
                for tool in mcp_tools:
                    tools_by_name[tool.name] = tool
                    self._tool_sources[tool_name].append(tool.name)
            except Exception as e:
                error_msg = f"Failed to connect: {str(e)}"
                self._disconnected_tools[tool_name] = error_msg
                logging.warning(f"Tool '{tool_name}' connection failed: {e}")

        return tools_by_name

    def _build_agents(self) -> "list[Agent]":
        """
        builds a list of agents based on the configuration
        """
        default_llm = self.get_llm_client()
        agents: "list[Agent]" = []
        self._agents_dict: "dict[str, Agent]" = {}
        self._tools_dict = self._build_tools()

        for name, cfg in self.agents_config.items():
            agent_tool_names = cfg.get("tools") or []
            agent_tools = []

            for tool_name in agent_tool_names:
                if tool_name in self._disconnected_tools:
                    logging.warning(
                        f"Agent '{name}' cannot use disconnected tool '{tool_name}': "
                        f"{self._disconnected_tools[tool_name]}"
                    )
                # check if it's an MCP server name (has multiple tools)
                elif tool_name in self._tool_sources:
                    for individual_tool_name in self._tool_sources[tool_name]:
                        agent_tools.append(self._tools_dict[individual_tool_name])
                elif tool_name in self._tools_dict:
                    agent_tools.append(self._tools_dict[tool_name])
                else:
                    logging.warning(
                        f"Agent '{name}' references unknown tool '{tool_name}'"
                    )

            # check if custom llm is used
            llm = (
                default_llm
                if not cfg.get("llmAPIURL")
                else self.get_llm_client(
                    cfg.get("llmAPIURL"),
                    os.getenv(cfg.get("llmAPIKeyEnvVar")),
                    cfg.get("model"),
                )
            )
            agent_kwargs = dict(config=cfg, llm=llm, tools=agent_tools)
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

    def cleanup(self) -> "bool":
        """
        cleans up MCP adapter connections
        """
        if not hasattr(self, "_mcp_adapters"):
            return True

        for adapter in self._mcp_adapters:
            try:
                adapter.__exit__(None, None, None)
            except Exception as e:
                logging.warning(f"Error closing MCP adapter: {e}")
                return False

        return True


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

        st.markdown("### Available Tools")

        if research_crew._tool_sources:
            for source_name, tool_list in research_crew._tool_sources.items():
                st.markdown(f"**{source_name}** :white_check_mark:")
                for tool_name in tool_list:
                    st.markdown(f"  - {tool_name}")

        if research_crew._disconnected_tools:
            st.markdown("**Disconnected Tools** :x:")
            for tool_name, error_msg in research_crew._disconnected_tools.items():
                st.markdown(f"  - {tool_name}")
                st.caption(f"    {error_msg}")

        if not research_crew._tool_sources and not research_crew._disconnected_tools:
            st.info("No tools connected")

    st.markdown("#### Crew overview")

    a_col, t_col = st.columns(2)
    with a_col:
        st.markdown("**Agents**")
        for agent_name, agent_config in research_crew.agents_config.items():
            agent = next(
                (a for a in crew_obj.agents if a.role == agent_config.get("role")), None
            )
            if agent:
                tool_sources = agent_config.get("tools", [])
                tools_info = (
                    f" (tools: {', '.join(tool_sources)})" if tool_sources else ""
                )
                st.markdown(f"- **{agent.role}** — goal: _{agent.goal}_{tools_info}")

    with t_col:
        st.markdown("**Tasks**")
        for task in crew_obj.tasks:
            st.markdown(f"- **{getattr(task, 'description', '')[:50]}...**")

    st.markdown("#### Run the crew")
    run_btn = st.button("🚀 Kick off")

    if run_btn:
        with st.spinner("Running crew..."):
            try:
                result, logs = run_crew(crew_obj, inputs={})
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
            finally:
                research_crew.cleanup()


if __name__ == "__main__":
    main()
