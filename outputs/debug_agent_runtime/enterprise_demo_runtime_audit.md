# Enterprise Demo Runtime Audit

## Current Runtime Entry Points

- `scripts/agent_cli.py` is the main LangGraph CLI entrypoint today.
- `scripts/ask_document.py` is still a separate QA-oriented CLI path.
- `scripts/list_documents.py` exists as a narrow utility entrypoint.
- `scripts/demo_agent_cli.py` does not currently exist.

## Current CLI Behavior

- `scripts/agent_cli.py` parses a large set of runtime flags for generation, planning, deep research, reflection, retrieval strategy, context, JSON, trace, and debug.
- It builds the full graph runtime directly inside the script through `build_agent_runtime(...)`.
- It prints answers and optional debug sections directly from script-level print helpers.
- It supports both one-shot execution and an interactive loop.

## Current Interactive Behavior

- Interactive mode already exists in `scripts/agent_cli.py` via `run_interactive_loop(...)`.
- The current prompt is always `document-agent>`.
- Prompt state does not reflect selected document or pending clarification.
- There is no slash-command application layer; all user input goes straight to the graph.
- There is no startup banner, status footer, runtime export flow, or enterprise presenter abstraction.

## Existing Agent Runtime Package

- `src/application/agent_runtime/` does not currently exist.
- Runtime concerns are currently split across:
  - `scripts/agent_cli.py`
  - `src/application/langgraph/memory/`
  - `src/application/langgraph/nodes/control/session_command_node.py`
  - `src/application/langgraph/routing/intent_router.py`
- This means runtime presentation, session UX, command UX, export UX, and graph bootstrap are not cleanly separated yet.

## Existing GraphResult / AgentState Data Available

- `GraphResult` already exposes:
  - `success`
  - `response_text`
  - `data`
  - `route`
  - `error_code`
  - `diagnostics`
  - `trace`
  - `messages`
- `AgentState` already carries rich runtime-safe information:
  - selected document fields
  - clarification state
  - planning outputs
  - retrieval strategy outputs
  - reflection outputs
  - research plan, evidence, report, and trace outputs
  - tool result payloads
  - `should_exit`
- `DocumentAgentGraph._build_result(...)` already materializes most of the runtime-safe surface needed by a presenter.

## Current ReAct Trace Data

- Safe graph node trace data already exists through `GraphRunRecorder` and `LangGraphTrace`.
- Current trace items include:
  - node name
  - route
  - elapsed time
  - tool name
  - plan identifiers
  - selected document id
  - diagnostics
- Deep research also records:
  - research plan
  - research trace
  - retrieval strategies per task
  - evidence counts per task
- This is enough to build safe ReAct-style presentation without exposing chain-of-thought.

## Current Presenter Responsibilities

- Presenter behavior is currently embedded inside `scripts/agent_cli.py`.
- Script functions currently handle:
  - answer printing
  - context chunk printing
  - retrieval strategy printing
  - research plan printing
  - reflection printing
  - JSON rendering
  - trace printing
- This is functional but mixes:
  - CLI orchestration
  - output formatting
  - partial runtime policy decisions

## Current Session Handling

- Session persistence already exists via:
  - `ConversationMemory`
  - `SessionStateStore`
- Persisted session state currently includes:
  - history
  - selected document id/title/file name
  - pending clarification
  - clarification options
  - clarification question
- This is useful, but it is graph-memory centric rather than an application runtime session model.
- Runtime-specific fields like last route, last trace, last research plan, last retrieval strategy, and runtime options are not modeled explicitly.

## Current Command Handling

- Command handling is currently graph-routed through `IntentRouter`.
- Existing session commands include:
  - help
  - exit
  - current document
  - clear document
  - list documents
  - open/select document variants
- `SessionCommandNode` formats command responses directly into `response_text`.
- There is no extensible command package, dispatcher, command result model, or slash-command layer.

## Current Output Problems

- Runtime formatting is concentrated in one large script.
- Interactive prompt is static and does not show document or clarification state.
- There is no startup banner or application identity.
- There is no dedicated status footer after each answer.
- There is no safe enterprise ReAct trace presentation layer.
- Export flow for professional demo traces does not exist.
- Command UX is not grouped or application-like.
- Interactive behavior still feels like a developer script rather than an enterprise assistant application.

## Architecture Gaps

- Missing `src/application/agent_runtime/` package.
- Missing demo-specific entrypoint script.
- Missing runtime session model distinct from graph memory.
- Missing command dispatcher and command result boundary.
- Missing dedicated presenters for console, markdown, and JSON.
- Missing safe ReAct trace builder/presenter.
- Missing export trace writer.
- Missing progress indicator layer for long-running operations.
- Missing runtime visibility policy for safe default output.

## Proposed Enterprise Runtime Architecture

- Keep `DocumentAgentGraph` and LangGraph as the execution engine.
- Add `src/application/agent_runtime/` as a thin application/runtime package.
- Responsibilities by package:
  - `demo_agent_runtime.py`
    - bootstrap interactive runtime
    - hold runtime dependencies
    - invoke graph
  - `session/`
    - runtime session model only
    - selected document, pending clarification, turn history, last trace metadata
  - `commands/`
    - slash-command parsing and dispatch
    - return `CommandResult`
    - no tool/repository/LLM direct calls outside approved boundaries
  - `react_loop/`
    - map `GraphResult` plus diagnostics into safe ReAct steps
    - deterministic thought summaries only
  - `presenters/`
    - startup banner
    - console rendering
    - markdown export
    - JSON export
  - `progress/`
    - lightweight terminal stage indicators
  - `policies/`
    - safe visibility toggles
  - `tracing/`
    - write professional trace exports

## Files Affected
| File | Current Responsibility | Problem | Proposed Change |
|---|---|---|---|
| `scripts/agent_cli.py` | Full CLI bootstrap, interactive loop, presenters, JSON rendering, graph execution | Too many responsibilities; not demo-runtime specific | Reuse logic selectively or delegate to new `agent_runtime` package; keep existing script stable |
| `scripts/demo_agent_cli.py` | Missing | Required demo entrypoint does not exist | Add dedicated enterprise demo CLI over existing graph runtime |
| `src/application/agent_runtime/` | Missing | No dedicated runtime package | Create grouped runtime package with clear boundaries |
| `src/application/langgraph/memory/conversation_memory.py` | Graph session memory persistence | Runtime session needs richer app-layer view | Reuse as backing persistence; wrap with runtime session manager |
| `src/application/langgraph/memory/session_state_store.py` | File-backed session store | Runtime-specific exports/options not modeled | Reuse through session manager, do not duplicate persistence logic unnecessarily |
| `src/application/langgraph/nodes/control/session_command_node.py` | Existing graph-side session commands | Response formatting is graph-side and limited | Preserve graph behavior; let runtime commands prefer application-friendly entrypoints where possible |
| `src/application/langgraph/routing/intent_router.py` | Natural-language and command route selection | No slash-command abstraction | Keep router as execution routing; add runtime slash-command dispatcher before graph invocation |
| `src/application/langgraph/graphs/document_agent_graph.py` | Main execution engine and result packaging | Already rich enough; should not gain presentation logic | Leave as engine; consume `GraphResult` from runtime layer |

## Implementation Phases

### Phase 1
- Create this audit.
- Confirm current entrypoints, graph result surface, trace surface, session surface, and architecture gaps.
- No runtime code changes yet.

### Phase 2
- Create `src/application/agent_runtime/`.
- Add runtime session model and command system.
- Add `scripts/demo_agent_cli.py`.
- Support interactive launch-once behavior and slash commands.

### Phase 3
- Add startup banner and pure presenters.
- Improve prompt rendering and status footer.
- Keep output safe and presentation-ready.

### Phase 4
- Add safe ReAct trace modeling and presentation.
- Build deterministic thought summaries from route/diagnostics only.

### Phase 5
- Add progress indicators for long-running operations.
- Keep them Windows-safe, quiet-safe, and JSON-safe.

### Phase 6
- Add Markdown/JSON trace export flow and `/export`.
- Write safe demo traces without raw prompts or internal reasoning.

### Phase 7
- Integrate everything, run runtime tests, CLI tests, LangGraph regression tests, and full pytest.
- Validate the manual demo flow stays polished and stable.
