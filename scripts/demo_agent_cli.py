from __future__ import annotations

"""
Enterprise interactive terminal runtime for the LangGraph document agent.

Usage:
    python scripts/demo_agent_cli.py
    python scripts/demo_agent_cli.py --interactive
    python scripts/demo_agent_cli.py "What are the maintenance intervals?" --document FWC12
"""

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Sequence
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for _import_root in (PROJECT_ROOT, SRC_ROOT):
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the enterprise interactive demo document agent.",
    )
    parser.add_argument(
        "user_input",
        nargs="?",
        help="Optional one-shot question or command.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run the interactive terminal application.",
    )
    parser.add_argument("--session-id", metavar="ID")
    parser.add_argument("--document", "-d", metavar="NAME")
    parser.add_argument("--document-id", metavar="ID")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--no-examples", action="store_true")
    parser.add_argument("--help-examples", action="store_true")
    parser.add_argument("--show-react", action="store_true")
    parser.add_argument("--deep-research", action="store_true")
    parser.add_argument("--reflection", action="store_true")
    parser.add_argument("--llm-planning", action="store_true")
    parser.add_argument("--retrieval-strategy", action="store_true")
    parser.add_argument("--write-trace", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args(list(argv) if argv is not None else None)


def build_session_id(session_id: str | None) -> str:
    return session_id or f"demo-{uuid4().hex[:12]}"


def should_start_interactive(args: argparse.Namespace) -> bool:
    return args.interactive or not args.user_input


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    interactive = should_start_interactive(args)

    app_session = None
    demo_agent = None
    try:
        from src.application.agent_runtime.commands import CommandDispatcher
        from src.application.agent_runtime.demo_agent import DemoAgent
        from src.application.agent_runtime.demo_agent_runtime import build_agent_runtime
        from src.application.agent_runtime.policies import DemoVisibilityPolicy
        from src.application.agent_runtime.presenters import (
            ConsolePresenter,
            JsonPresenter,
            MarkdownPresenter,
            StartupBanner,
        )
        from src.application.agent_runtime.react_loop import ReactTraceBuilder
        from src.application.agent_runtime.session import RuntimeOptions, SessionManager
        from src.application.agent_runtime.tracing import DemoTraceWriter
        from src.bootstrap.startup import bootstrap_application
        from src.config.settings import ingestion_settings
        from src.infrastructure.db.base import Base
        from src.infrastructure.db.schema_management import ensure_database_schema
        from src.infrastructure.db.orm_models import __all__ as _orm_models_loaded
        from src.infrastructure.db.session import SessionLocal, engine

        bootstrap_application()
        ensure_database_schema(engine)
        app_session = SessionLocal()

        runtime = build_agent_runtime(
            app_session,
            enable_generation=ingestion_settings.enable_answer_generation,
            enable_llm_planning=args.llm_planning,
            enable_llm_research_planning=args.llm_planning,
        )
        runtime_options = RuntimeOptions(
            quiet=args.quiet,
            no_examples=args.no_examples,
            help_examples=args.help_examples,
            show_react=args.show_react,
            deep_research=args.deep_research,
            reflection=args.reflection,
            llm_planning=args.llm_planning,
            retrieval_strategy=args.retrieval_strategy,
            write_trace=args.write_trace,
            debug=args.debug,
            json_output=args.json,
        )
        session_id = build_session_id(args.session_id)
        session_manager = SessionManager()
        session_snapshot = runtime.load_session_snapshot(session_id)
        session = session_manager.create_session(
            session_id=session_id,
            runtime_options=runtime_options,
            snapshot=session_snapshot,
        )
        presenter = ConsolePresenter()
        json_presenter = JsonPresenter()
        trace_writer = DemoTraceWriter(
            markdown_presenter=MarkdownPresenter(),
            json_presenter=json_presenter,
        )
        demo_agent = DemoAgent(
            runtime=runtime,
            session=session,
            session_manager=session_manager,
            command_dispatcher=CommandDispatcher(),
            trace_builder=ReactTraceBuilder(),
            visibility_policy=DemoVisibilityPolicy(debug=args.debug),
            trace_writer=trace_writer,
        )
        banner_text = StartupBanner().render(
            runtime_status=runtime.runtime_status,
            selected_document_name=session.selected_document.display_name,
            quiet=args.quiet or args.json,
            no_examples=args.no_examples,
        )
        if banner_text:
            print(banner_text)

        initial_selection = demo_agent.initialize_document(
            document_id=args.document_id,
            document_query=args.document,
        )
        if initial_selection is not None and not args.json and not args.quiet:
            if initial_selection.graph_result is not None:
                print(
                    presenter.render_command_result(
                        _initial_selection_command_result(initial_selection.graph_result),
                        session=session,
                        policy=demo_agent.visibility_policy,
                    )
                )

        if interactive:
            pending_inputs = [args.user_input] if args.user_input else []
            while True:
                if pending_inputs:
                    user_input = pending_inputs.pop(0)
                else:
                    try:
                        user_input = input(session.prompt_text()).strip()
                    except EOFError:
                        print()
                        return 0
                    except KeyboardInterrupt:
                        print("\nInterrupted.")
                        return 1
                if not user_input:
                    continue
                handled = demo_agent.process_input(user_input)
                if args.json:
                    print(_interactive_json_payload(handled, session, json_presenter))
                else:
                    _print_handled_result(
                        handled,
                        presenter=presenter,
                        session=session,
                        show_react=args.show_react,
                        policy=demo_agent.visibility_policy,
                    )
                if handled.should_exit:
                    return 0

        if not args.user_input:
            print("Provide a question or use --interactive.", file=sys.stderr)
            return 1

        handled = demo_agent.process_input(args.user_input)
        if args.json:
            if handled.graph_result is not None:
                print(
                    json.dumps(
                        json_presenter.render(
                            session=session,
                            result=handled.graph_result,
                            react_trace=handled.react_trace,
                            include_trace=args.show_react,
                        ),
                        indent=2,
                    )
                )
            elif handled.command_result is not None:
                print(
                    json.dumps(
                        {
                            "success": handled.command_result.success,
                            "message": handled.command_result.message,
                            "data": handled.command_result.data,
                            "should_exit": handled.command_result.should_exit,
                        },
                        indent=2,
                        default=str,
                    )
                )
        else:
            _print_handled_result(
                handled,
                presenter=presenter,
                session=session,
                show_react=args.show_react,
                policy=demo_agent.visibility_policy,
            )
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        if demo_agent is not None:
            demo_agent.close()
        elif app_session is not None:
            app_session.close()


def _print_handled_result(
    handled,
    *,
    presenter,
    session,
    show_react: bool,
    policy,
) -> None:
    if handled.command_result is not None:
        print(
            presenter.render_command_result(
                handled.command_result,
                session=session,
                policy=policy,
            )
        )
    elif handled.graph_result is not None:
        print(
            presenter.render_graph_result(
                user_input=_latest_user_prompt(session),
                result=handled.graph_result,
                react_trace=handled.react_trace,
                session=session,
                policy=policy,
                show_react=show_react,
            )
        )
    if handled.export_paths:
        print(presenter.render_command_result(
            _export_command_result(handled.export_paths),
            session=session,
            policy=policy,
        ))


def _latest_user_prompt(session) -> str:
    turns = session.conversation_history.turns
    for turn in reversed(turns):
        if getattr(turn, "role", "") == "user":
            return str(getattr(turn, "content", ""))
    return ""


def _export_command_result(export_paths: dict[str, str]):
    from src.application.agent_runtime.commands import CommandResult

    return CommandResult(
        success=True,
        message="Trace saved:",
        data=export_paths,
        render_as="export",
    )


def _initial_selection_command_result(graph_result):
    from src.application.agent_runtime.commands import CommandResult

    data = graph_result.data or {}
    return CommandResult(
        success=graph_result.success,
        message="Selected document",
        data={
            "selected_document": {
                "title": data.get("selected_document_title") or data.get("document_title"),
                "file_name": data.get("selected_document_file_name"),
            }
        },
        render_as="document_selected",
    )


def _interactive_json_payload(handled, session, json_presenter) -> str:
    if handled.graph_result is not None:
        return json.dumps(
            json_presenter.render(
                session=session,
                result=handled.graph_result,
                react_trace=handled.react_trace,
                include_trace=True,
            ),
            indent=2,
        )
    command_result = handled.command_result
    return json.dumps(
        {
            "success": command_result.success if command_result is not None else False,
            "message": command_result.message if command_result is not None else "",
            "data": command_result.data if command_result is not None else {},
            "should_exit": command_result.should_exit if command_result is not None else False,
        },
        indent=2,
        default=str,
    )


if __name__ == "__main__":
    raise SystemExit(main())
