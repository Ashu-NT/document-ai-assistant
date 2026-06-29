# LangGraph V2 Audit

## Current V1 Capabilities
- `list_documents` route
  - Node: `ListDocumentsNode`
  - Tool called: `list_documents`
- `find_document` route
  - Node: `FindDocumentNode`
  - Tool called: `find_document`
- `document_details` route
  - Node: `DocumentDetailsNode`
  - Tool called: `document_details`
- `document_exploration` route
  - Nodes: `FindDocumentNode` optionally, then `ExploreDocumentNode`
  - Tool called: `explore_document`
- `retrieve_evidence` route
  - Nodes: `FindDocumentNode` optionally, then `RetrieveEvidenceNode`
  - Tool called: `retrieve_chunks`
- `answer_question` route
  - Nodes: `FindDocumentNode` optionally, then `AnswerQuestionNode`
  - Tool called: `answer_question`
- `quality_gate` route
  - Node: `RunQualityGateNode`
  - Tool called: `run_quality_gate`
- `retrieval_trace` route
  - Nodes: `FindDocumentNode` optionally, then `RetrievalTraceNode`
  - Tool called: `retrieval_trace`
- Clarification/error/final formatting
  - Nodes: `ClarifyRequestNode`, `ErrorHandlerNode`, `FinalResponseNode`

## Current State Handling
- State container:
  - `src/application/langgraph/state/agent_state.py`
  - Current fields cover one request only: user input, route, document query/id/title, question, flags, tool results, response, error, clarification message, trace, conversation id, history
- What state exists today:
  - `document_id`, `document_query`, `document_title`
  - `needs_clarification`, `clarification_message`
  - `trace`
  - `history`
- What memory exists:
  - `ConversationMemory` is an in-process deque only
  - It stores recent user/assistant messages with timestamps
  - It has no document selection state
  - It has no pending clarification state
  - It has no persistence layer
- What is lost between CLI calls:
  - selected/current document
  - clarification candidates/options
  - pending clarification question
  - conversation history
  - any session identity
- Why it is lost:
  - `scripts/agent_cli.py` creates a fresh runtime and fresh `ConversationMemory(max_messages=20)` every process invocation
  - there is no `SessionStateStore`
  - `DocumentAgentGraph.run()` only accepts transient request options

## Missing V2 Capabilities
- selected document memory
  - no `selected_document_id/title/file_name` fields in `AgentState`
  - no session-backed state store
- clarification pending state
  - `ClarifyRequestNode` only echoes a message
  - no stored options, no candidate index, no resume behavior
- multi-turn CLI session loop
  - `agent_cli.py` is one-shot only
  - no `--interactive`
  - no `--session-id`
- command handling for open/current/clear
  - router currently supports `find/open document ...` but not session-style `open FWC12`
  - no `current document`, `clear document`, `help`, or `exit` routes
- numeric clarification response
  - no route for `1`, `2`, `3`
  - no stateful mapping from numeric response to stored candidates

## Affected Files
| Area | File | Change |
|---|---|---|
| Routing | `src/application/langgraph/routing/route_type.py` | Add session/control route types |
| Routing | `src/application/langgraph/routing/route_decision.py` | Add session/current-document/clarification metadata |
| Routing | `src/application/langgraph/routing/intent_router.py` | Add deterministic patterns for select/current/clear/help/exit/clarification |
| State | `src/application/langgraph/state/agent_state.py` | Add selected-document and pending-clarification session fields |
| Memory | `src/application/langgraph/memory/conversation_memory.py` | Add session-aware load/save path and selected-document support |
| Memory | `src/application/langgraph/memory/session_state_store.py` | New store for session persistence |
| Control node | `src/application/langgraph/nodes/control/route_request_node.py` | Thread richer route decision fields into state |
| Control node | `src/application/langgraph/nodes/control/clarify_request_node.py` | Support stored clarification options and numeric responses |
| Control node | `src/application/langgraph/nodes/control/final_response_node.py` | Persist small session state and expose selected document info |
| Document node | `src/application/langgraph/nodes/documents/find_document_node.py` | Set selected document on single hit; preserve options on multi-hit |
| Document node | `src/application/langgraph/nodes/documents/document_details_node.py` | Fall back to current selected document |
| QA nodes | `src/application/langgraph/nodes/question_answering/answer_question_node.py` | Use current selected document when appropriate |
| QA nodes | `src/application/langgraph/nodes/question_answering/explore_document_node.py` | Use current selected document for `explore it` style requests |
| QA nodes | `src/application/langgraph/nodes/question_answering/retrieve_evidence_node.py` | Use current selected document when appropriate |
| Graph | `src/application/langgraph/graphs/document_agent_graph.py` | Add pending clarification + session command flow |
| Factory | `src/application/langgraph/factories/graph_factory.py` | Accept memory/store dependencies |
| CLI | `scripts/agent_cli.py` | Add `--session-id`, `--interactive`, loop behavior, session continuity |
| Validation | `src/application/langgraph/validation/graph_request_validator.py` | Validate session id and clarification input |
| Validation | `src/application/langgraph/validation/graph_state_validator.py` | New validator for selected-document/clarification state consistency |
| Tests | `tests/unit/application/langgraph/` | Extend routing, memory, node, graph coverage for stateful V2 |
| Tests | `tests/unit/cli_scripts/test_agent_cli.py` | Add interactive/session-state CLI coverage |

## V2 Implementation Plan
1. Extend routing contracts first.
   - Add new `RouteType` values.
   - Extend `RouteDecision` with state/session metadata.
   - Update `IntentRouter` to detect select/current/clear/help/exit and numeric clarification responses.
2. Add state and session persistence.
   - Expand `AgentState`.
   - Implement `SessionStateStore`.
   - Upgrade `ConversationMemory` to load/save lightweight session state.
3. Upgrade clarification flow.
   - Preserve candidate options in state.
   - Resolve numeric responses deterministically.
   - Clear clarification state after successful selection.
4. Update graph and nodes.
   - Make document selection explicit state.
   - Let detail/explore/retrieve/answer paths consume current selected document.
   - Keep existing V1 direct one-shot paths working.
5. Update CLI last.
   - Add `--session-id` and `--interactive`.
   - Preserve one-shot behavior.
   - Print selected-document and clarification information cleanly.
6. Add validation and tests.
   - Cover routing, memory, graph flow, CLI loop, and override precedence.
