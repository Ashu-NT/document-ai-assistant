from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.application.agent_runtime.commands import CommandDispatcher, CommandResult
from src.application.agent_runtime.demo_agent_runtime import (
    AgentRuntime,
    close_agent_runtime,
)
from src.application.agent_runtime.policies import DemoVisibilityPolicy
from src.application.agent_runtime.react_loop import ReactTrace, ReactTraceBuilder
from src.application.agent_runtime.session import Session, SessionManager
from src.application.agent_runtime.streaming import ConsoleLiveEventSink, NullEventSink
from src.application.agent_runtime.tracing import DemoTraceWriter


@dataclass(slots=True)
class HandledInputResult:
    command_result: CommandResult | None = None
    graph_result: Any | None = None
    react_trace: ReactTrace | None = None
    export_paths: dict[str, str] | None = None

    @property
    def should_exit(self) -> bool:
        if self.command_result is not None:
            return self.command_result.should_exit
        data = getattr(self.graph_result, "data", {}) or {}
        return bool(data.get("should_exit"))


class DemoAgent:
    def __init__(
        self,
        *,
        runtime: AgentRuntime,
        session: Session,
        session_manager: SessionManager,
        command_dispatcher: CommandDispatcher,
        trace_builder: ReactTraceBuilder,
        visibility_policy: DemoVisibilityPolicy,
        trace_writer: DemoTraceWriter,
    ) -> None:
        self.runtime = runtime
        self.session = session
        self.session_manager = session_manager
        self.command_dispatcher = command_dispatcher
        self.trace_builder = trace_builder
        self.visibility_policy = visibility_policy
        self.trace_writer = trace_writer

    def initialize_document(
        self,
        *,
        document_id: str | None,
        document_query: str | None,
    ) -> HandledInputResult | None:
        if not document_id and not document_query:
            return None
        if document_query:
            result = self.execute_graph_command(f"open {document_query}", session=self.session)
        else:
            result = self.runtime.run_graph_request(
                "find document",
                document_id=document_id,
                document_query=None,
                session_id=self.session.session_id,
                allow_answer_generation=False,
                include_context=False,
                llm_planning_enabled=self.session.runtime_options.llm_planning,
                deep_research_enabled=self.session.runtime_options.deep_research,
                llm_research_planning_enabled=self.session.runtime_options.llm_planning,
                reflection_enabled=self.session.runtime_options.reflection,
                retrieval_strategy_enabled=self.session.runtime_options.retrieval_strategy,
            )
            react_trace = self.trace_builder.build(
                user_input="find document",
                result=result,
                policy=self.visibility_policy,
            )
            self.session_manager.update_from_graph_result(
                self.session,
                result=result,
                react_trace=react_trace,
            )
        react_trace = self.session.last_trace
        return HandledInputResult(
            graph_result=self.session.last_result,
            react_trace=react_trace,
        )

    def process_input(self, user_input: str) -> HandledInputResult:
        command_result = self.command_dispatcher.dispatch(
            user_input,
            agent=self,
            session=self.session,
        )
        if command_result is not None:
            if command_result.update_session:
                graph_result = command_result.data.get("graph_result")
                if graph_result is not None:
                    react_trace = self.trace_builder.build(
                        user_input=user_input,
                        result=graph_result,
                        policy=self.visibility_policy,
                    )
                    self.session_manager.update_from_graph_result(
                        self.session,
                        result=graph_result,
                        react_trace=react_trace,
                    )
                    return HandledInputResult(
                        command_result=command_result,
                        graph_result=graph_result,
                        react_trace=react_trace,
                    )
            return HandledInputResult(command_result=command_result)

        result = self.execute_graph_command(user_input, session=self.session)
        export_paths = None
        if self.session.runtime_options.write_trace and self.session.last_trace is not None:
            export_paths = self.export_latest_trace(self.session)
        return HandledInputResult(
            graph_result=result,
            react_trace=self.session.last_trace,
            export_paths=export_paths,
        )

    def execute_graph_command(self, user_input: str, *, session: Session):
        opts = session.runtime_options
        if opts.quiet or opts.json_output:
            sink = NullEventSink()
        else:
            import sys
            sink = ConsoleLiveEventSink(stream=sys.stdout)

        result = self.runtime.run_graph_request(
            user_input,
            document_id=None,
            document_query=None,
            session_id=session.session_id,
            allow_answer_generation=bool(
                self.runtime.runtime_settings.get("generation_enabled", False)
            ),
            include_context=False,
            llm_planning_enabled=opts.llm_planning,
            deep_research_enabled=opts.deep_research,
            llm_research_planning_enabled=opts.llm_planning,
            reflection_enabled=opts.reflection,
            show_reflection=opts.reflection,
            retrieval_strategy_enabled=opts.retrieval_strategy,
            llm_retrieval_strategy_enabled=opts.retrieval_strategy,
            event_sink=sink,
        )
        react_trace = self.trace_builder.build(
            user_input=user_input,
            result=result,
            policy=self.visibility_policy,
        )
        self.session_manager.update_from_graph_result(
            session,
            result=result,
            react_trace=react_trace,
        )
        return result

    def extract_list_documents(self, result) -> list[dict[str, Any]]:
        data = result.data or {}
        tool_results = data.get("tool_results") or {}
        payload = (tool_results.get("list_documents") or {}).get("data")
        if isinstance(payload, list):
            return [dict(item) for item in payload if isinstance(item, dict)]
        return []

    def extract_selected_document(self, result) -> dict[str, Any]:
        data = result.data or {}
        return {
            "document_id": data.get("selected_document_id") or data.get("document_id"),
            "title": data.get("selected_document_title") or data.get("document_title"),
            "file_name": data.get("selected_document_file_name"),
        }

    def export_latest_trace(self, session: Session) -> dict[str, str] | None:
        if session.last_result is None or session.last_trace is None:
            return None
        return self.trace_writer.write_latest_trace(
            session=session,
            result=session.last_result,
            react_trace=session.last_trace,
        )

    def build_status_payload(self, session: Session) -> dict[str, Any]:
        return {
            "session_id": session.session_id,
            "selected_document": session.selected_document.display_name,
            "last_route": session.last_route,
            "started_at": session.started_at,
            "updated_at": session.updated_at,
            "document_count": self.runtime.runtime_status.document_count,
            "model": self.runtime.runtime_status.model_name,
        }

    def build_settings_payload(self, session: Session) -> dict[str, Any]:
        return {
            "quiet": session.runtime_options.quiet,
            "show_react": session.runtime_options.show_react,
            "deep_research": session.runtime_options.deep_research,
            "reflection": session.runtime_options.reflection,
            "llm_planning": session.runtime_options.llm_planning,
            "retrieval_strategy": session.runtime_options.retrieval_strategy,
            "write_trace": session.runtime_options.write_trace,
            "debug": session.runtime_options.debug,
            "general_llm": self.runtime.runtime_settings.get("general_llm"),
            "planning_llm": self.runtime.runtime_settings.get("planning_llm"),
            "ollama_base_url": self.runtime.runtime_settings.get("ollama_base_url"),
        }

    def reset_session(self, session: Session) -> None:
        self.runtime.clear_persisted_session(session.session_id)
        self.session_manager.reset(session)

    def close(self) -> None:
        close_agent_runtime(self.runtime)


