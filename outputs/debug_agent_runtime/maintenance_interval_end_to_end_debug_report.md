# Maintenance Interval End-to-End Debug Report

## 1. Reproduction

Command:

```powershell
python scripts/demo_agent_cli.py --interactive --document "19P006-31-FWC12-5-1-0_Manual" --show-react --reflection --deep-research --llm-planning
```

Interactive query:

```text
What are the maintenance intervals?
```

Observed target failure:

- Duplicate console presentation: `Agent Loop` and `Agent Trace`
- Wrong retrieval strategy: `MAINTENANCE_LOOKUP` plus `TECHNICAL_SPECIFICATION`
- Maintenance answer pollution with technical specifications
- Reflection too permissive
- Live stream missing retrieve/observation steps for `answer_question`
- Advisor rejection not explained clearly in the user-facing trace

## 2. Current Runtime Flow

Active runtime path:

1. Interactive input is read in [`scripts/demo_agent_cli.py`](../../scripts/demo_agent_cli.py) via `main()` and `input()` in `main()` when `--interactive` is enabled.
2. The CLI delegates to `DemoAgent.process_input()` in [`src/application/agent_runtime/demo_agent.py`](../../src/application/agent_runtime/demo_agent.py).
3. `CommandDispatcher.dispatch()` handles explicit session commands first. If no command matches, `DemoAgent.execute_graph_command()` runs the LangGraph runtime.
4. `DemoAgent.execute_graph_command()` always creates a `ConsoleLiveEventSink` when the session is not `quiet` and not `json_output`.
5. `AgentRuntime.run_graph_request()` in [`src/application/agent_runtime/demo_agent_runtime.py`](../../src/application/agent_runtime/demo_agent_runtime.py) forwards the request to `DocumentAgentGraph.run()`.
6. `DocumentAgentGraph.run()` in [`src/application/langgraph/graphs/document_agent_graph.py`](../../src/application/langgraph/graphs/document_agent_graph.py):
   - builds the initial `AgentState` with `build_agent_state()`
   - restores session memory if present
   - validates request and state
   - appends the user message to memory
   - invokes the compiled LangGraph through `_invoke()`
7. `_invoke()` uses `EventStreamAdapter.run()` in [`src/application/agent_runtime/streaming/event_stream_adapter.py`](../../src/application/agent_runtime/streaming/event_stream_adapter.py) when an event sink is present.
8. The first graph node is `RouteRequestNode.__call__()` in [`src/application/langgraph/nodes/control/route_request_node.py`](../../src/application/langgraph/nodes/control/route_request_node.py). That node:
   - calls `IntentRouter.route()` in [`src/application/langgraph/routing/intent_router.py`](../../src/application/langgraph/routing/intent_router.py)
   - applies pre-route guardrails through `PreRouteGuardrailService`
   - optionally invokes the guarded route-level `StrategyAdvisor`
9. For this query, the route falls through to `RouteType.ANSWER_QUESTION`.
10. The graph enters `AnswerQuestionNode.__call__()` in [`src/application/langgraph/nodes/question_answering/answer_question_node.py`](../../src/application/langgraph/nodes/question_answering/answer_question_node.py).
11. Inside `AnswerQuestionNode`, when retrieval strategy is enabled:
   - `RetrievalStrategyService.select_and_plan()` in [`src/application/langgraph/retrieval_strategy/services/retrieval_strategy_service.py`](../../src/application/langgraph/retrieval_strategy/services/retrieval_strategy_service.py) runs query analysis, signal extraction, deterministic strategy selection, optional advisor merge, strategy validation, and plan building
   - `RetrievalPlanExecutor.execute()` executes one or more retrieval steps
   - the merged evidence is passed into `AnswerQuestionTool` as `context_override_chunks`
12. `AnswerQuestionTool.run()` in [`src/application/tools/question_answering/answer_question_tool.py`](../../src/application/tools/question_answering/answer_question_tool.py) delegates to `QuestionAnsweringWorkflow.run()`.
13. `QuestionAnsweringWorkflow.run()` in [`src/application/workflows/question_answering/question_answering_workflow.py`](../../src/application/workflows/question_answering/question_answering_workflow.py):
   - runs pre-query guardrails
   - routes to retrieval QA
   - runs retrieval or uses `context_override_chunks`
   - runs context guardrails
   - runs pre-generation guardrails
   - calls `AnswerGenerationService.generate()` if generation is enabled
14. `AnswerGenerationService.generate()` in [`src/application/services/answer_generation/answer_generation_service.py`](../../src/application/services/answer_generation/answer_generation_service.py):
   - resolves answer intent
   - organizes structured answer context
   - resolves an `AnswerFormatPolicy`
   - builds the prompt through `AnswerPromptBuilder.build()` in [`src/application/prompts/answer_generation/answer_prompt_builder.py`](../../src/application/prompts/answer_generation/answer_prompt_builder.py)
   - calls `LLMService.generate()`
15. If reflection is enabled, the graph enters `ReflectAnswerNode.__call__()` in [`src/application/langgraph/nodes/question_answering/reflect_answer_node.py`](../../src/application/langgraph/nodes/question_answering/reflect_answer_node.py), which delegates to `ReflectionService.review()` in [`src/application/langgraph/reflection/services/reflection_service.py`](../../src/application/langgraph/reflection/services/reflection_service.py).
16. `FinalResponseNode.__call__()` in [`src/application/langgraph/nodes/control/final_response_node.py`](../../src/application/langgraph/nodes/control/final_response_node.py) resolves the final response text and runs the post-response guardrail.
17. `DocumentAgentGraph._build_result()` builds the final `GraphResult`.
18. `DemoAgent` separately builds a post-run `ReactTrace` through `ReactTraceBuilder.build()` in [`src/application/agent_runtime/react_loop/react_trace_builder.py`](../../src/application/agent_runtime/react_loop/react_trace_builder.py).
19. `ConsolePresenter.render_graph_result()` in [`src/application/agent_runtime/presenters/console_presenter.py`](../../src/application/agent_runtime/presenters/console_presenter.py) prints:
   - `User Request`
   - optional post-run `Agent Trace`
   - `Final Answer`
   - footer

## 3. Duplicate Output Root Cause

### Which component prints `Agent Loop`

- `ConsoleLiveEventSink._ensure_header()` in [`src/application/agent_runtime/streaming/console_event_sink.py`](../../src/application/agent_runtime/streaming/console_event_sink.py)

### Which component prints `Agent Trace`

- `ConsolePresenter.render_graph_result()` in [`src/application/agent_runtime/presenters/console_presenter.py`](../../src/application/agent_runtime/presenters/console_presenter.py)
- The trace content itself is built by `ReactTraceBuilder.build()`

### Which flags control them

- `Agent Loop` is not actually controlled by `--show-react`
- `DemoAgent.execute_graph_command()` always installs `ConsoleLiveEventSink` unless `quiet` or `json_output` is enabled
- `Agent Trace` is controlled by `show_react=True` passed from `scripts/demo_agent_cli.py`

### Why both are enabled

- Live streaming is always on in normal interactive CLI mode
- `--show-react` separately enables post-run trace rendering
- So `--show-react` means:
  - live stream already prints `Agent Loop`
  - final presenter additionally prints `Agent Trace`

### Root cause summary

There is no single presentation owner. The live sink owns one trace-like view, and the final presenter independently owns another.

### Expected fix direction

- Normal interactive mode:
  - keep live `Agent Loop`
  - suppress post-run `Agent Trace`
- Debug/export mode:
  - allow post-run trace separately

Likely touch points:

- [`src/application/agent_runtime/demo_agent.py`](../../src/application/agent_runtime/demo_agent.py)
- [`scripts/demo_agent_cli.py`](../../scripts/demo_agent_cli.py)
- [`src/application/agent_runtime/presenters/console_presenter.py`](../../src/application/agent_runtime/presenters/console_presenter.py)

## 4. Missing Live Retrieve / Observation Root Cause

### What currently happens

- `EventStreamAdapter` maps whole LangGraph node completions to live events
- For `answer_question` route, retrieval happens inside `AnswerQuestionNode.__call__()`
- There is no separate graph node for retrieval in that route

### Current mapping problem

In [`src/application/agent_runtime/streaming/event_stream_adapter.py`](../../src/application/agent_runtime/streaming/event_stream_adapter.py):

- `route_request` -> `UNDERSTAND_REQUEST`
- `answer_question` -> `FINAL_STARTED`
- `reflect_answer` -> `REFLECTION_COMPLETED`

But:

- `FINAL_STARTED` is explicitly silent in `ConsoleLiveEventSink`
- `answer_question` does not emit a retrieval event even though it internally runs retrieval strategy planning and retrieval execution

### Payload extraction problem

For `ACTION_COMPLETED`, `_extract_payload()` looks at `state.get("context_chunks")`.

That field is not the real QA retrieval handoff field for this route. `AnswerQuestionNode` stores:

- `initial_context_chunks`
- `merged_context_chunks`
- `merged_chunk_ids`
- `retrieval_strategy_decision`
- `retrieval_execution_result`

So even if the node were mapped differently, the current payload extractor would still miss the QA retrieval context.

### Root cause summary

- Wrong event boundary: retrieval is hidden inside `answer_question`
- Wrong event mapping: `answer_question` maps to a silent `FINAL_STARTED`
- Wrong payload source: `context_chunks` is not the active QA retrieval field

### Expected fix direction

Either:

1. emit explicit retrieval and observation metadata from `AnswerQuestionNode`, or
2. teach `EventStreamAdapter` to derive retrieve/observation events from `answer_question` node output

Likely touch points:

- [`src/application/langgraph/nodes/question_answering/answer_question_node.py`](../../src/application/langgraph/nodes/question_answering/answer_question_node.py)
- [`src/application/agent_runtime/streaming/event_stream_adapter.py`](../../src/application/agent_runtime/streaming/event_stream_adapter.py)
- [`src/application/agent_runtime/streaming/console_event_sink.py`](../../src/application/agent_runtime/streaming/console_event_sink.py)

## 5. Strategy Selection Root Cause

### Active strategy pipeline

- `RetrievalQueryAnalyzer.analyze()` in [`src/application/workflows/retrieval/retrieval_query_analyzer.py`](../../src/application/workflows/retrieval/retrieval_query_analyzer.py)
- `RetrievalSignalExtractor.extract()` in [`src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py`](../../src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py)
- `DeterministicStrategySelector.select()` in [`src/application/langgraph/retrieval_strategy/selectors/deterministic_strategy_selector.py`](../../src/application/langgraph/retrieval_strategy/selectors/deterministic_strategy_selector.py)
- optional advisor merge in `RetrievalStrategyService.select_and_plan()`
- plan building in `RetrievalPlanBuilder.build()` in [`src/application/langgraph/retrieval_strategy/planners/retrieval_plan_builder.py`](../../src/application/langgraph/retrieval_strategy/planners/retrieval_plan_builder.py)

### Why `TECHNICAL_SPECIFICATION` appears for this maintenance query

This is caused by two concrete issues in the deterministic path.

#### A. Maintenance queries currently whitelist `ChunkType.TECHNICAL_SPECIFICATION`

In [`src/application/workflows/retrieval/retrieval_query_chunk_type_preference_mapper.py`](../../src/application/workflows/retrieval/retrieval_query_chunk_type_preference_mapper.py), the `RetrievalQueryIntent.MAINTENANCE` branch includes:

- `ChunkType.MAINTENANCE_INTERVAL`
- `ChunkType.MAINTENANCE_PROCEDURE`
- `ChunkType.SPARE_PARTS_TABLE`
- `ChunkType.TECHNICAL_SPECIFICATION`

For interval-like maintenance questions, the narrowed preference list still includes `ChunkType.TECHNICAL_SPECIFICATION`.

That means the strategy stack is allowed to treat specification as a legitimate supporting category before any later filtering happens.

#### B. The specification signal extractor contains low-precision lexical triggers

In [`src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py`](../../src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py), `_SPECIFICATION_TERMS` contains:

- `" v"`
- `" a"`

The query `what are the maintenance intervals?` contains the substring `" a"` inside `what are`.

So the query receives an accidental specification keyword signal even though the user did not ask for specifications.

#### C. Why that becomes a secondary strategy instead of `TABLE_LOOKUP`

For this query, the effective deterministic scoring is roughly:

- `MAINTENANCE_LOOKUP`
  - `maintenance` keyword signals
  - `interval` keyword signals
  - maintenance-related chunk-type signals
- `TECHNICAL_SPECIFICATION`
  - accidental `" a"` specification keyword signal
  - `chunk_type:technical_specification`
- `TABLE_LOOKUP`
  - usually only `chunk_type:spare_parts_table`
  - no explicit `table` or `schedule` lexical signal from the raw user wording

`DeterministicStrategySelector` allows secondaries when score `>= 4.0`. Because the false specification signal adds to the specification chunk-type signal, `TECHNICAL_SPECIFICATION` can cross the secondary threshold while `TABLE_LOOKUP` stays below it.

### Advisor impact

The guarded advisor is not the main root cause for this case.

- `RouteRequestNode` stores advisor outcome in `strategy_advisor_result`
- `RetrievalStrategyService` can also call the advisor for retrieval strategy selection
- But the deterministic path already contains the false-positive specification signal and the permissive maintenance chunk-type preference

### Root cause summary

The wrong secondary strategy is caused by deterministic retrieval logic, not by answer generation:

- maintenance interval queries currently allow technical-spec chunk types too early
- specification keyword detection is too broad and accidentally matches ordinary English text

### Expected fix direction

- remove low-precision specification markers like `" a"` and `" v"`
- make maintenance interval queries prefer `TABLE_LOOKUP`
- stop injecting `TECHNICAL_SPECIFICATION` into maintenance interval chunk-type preferences unless the query explicitly asks for specs
- keep `PROCEDURE_LOOKUP` optional only when procedure wording is present

Likely touch points:

- [`src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py`](../../src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py)
- [`src/application/workflows/retrieval/retrieval_query_chunk_type_preference_mapper.py`](../../src/application/workflows/retrieval/retrieval_query_chunk_type_preference_mapper.py)
- [`src/application/langgraph/retrieval_strategy/selectors/deterministic_strategy_selector.py`](../../src/application/langgraph/retrieval_strategy/selectors/deterministic_strategy_selector.py)

## 6. Retrieval Pollution Root Cause

### Where the pollution enters

Once `TECHNICAL_SPECIFICATION` is selected as a secondary strategy:

- `RetrievalPlanBuilder.build()` creates an extra retrieval step
- that step uses technical-spec-oriented query expansion
- that step searches technical-spec chunk types

So the off-intent evidence enters before answer generation.

### Why it survives

The current guardrails do not remove intent-mismatched technical-spec chunks for maintenance interval questions.

Current context guardrails in the active runtime:

- `ScopedDocumentConsistencyGuardrail`
- `ContextFilteringGuardrail`
- `ContextQualityGuardrail`
- `ContextBudgetGuardrail`

But `ContextFilteringGuardrail` in [`src/application/guardrails/context/context_filtering_guardrail.py`](../../src/application/guardrails/context/context_filtering_guardrail.py) only removes:

- TOC chunks
- obvious noise chunks
- branding/copyright chunks

It does not reject chunks because they are off-intent for maintenance interval QA.

`ContextQualityGuardrail` and `ContextBudgetGuardrail` only enforce minimum evidence and size budget. They do not perform semantic intent filtering.

### Merger behavior

`RetrievalEvidenceMerger.merge()` in [`src/application/langgraph/retrieval_strategy/services/retrieval_evidence_merger.py`](../../src/application/langgraph/retrieval_strategy/services/retrieval_evidence_merger.py):

- deduplicates only by `chunk_id`
- sorts by:
  - whether the chunk came from the primary strategy
  - score
  - page order

It does not add a negative penalty for technical-spec chunks when the primary user need is maintenance intervals.

### Context expansion impact

`RetrievalContextExpander` in [`src/application/workflows/retrieval/retrieval_context_expander.py`](../../src/application/workflows/retrieval/retrieval_context_expander.py) can add same-family or nearby context after anchor retrieval. It is not the first root cause here. The main issue is that the anchor set is already polluted before expansion.

### Root cause summary

Technical-spec chunks are allowed into the retrieval plan, survive context guardrails, and are merged without an intent-aware downgrade.

### Expected fix direction

- repair strategy selection first
- add maintenance-intent evidence filtering or reranking penalties for technical-spec chunks
- make maintenance interval questions prefer maintenance interval, maintenance procedure, and table evidence

Likely touch points:

- [`src/application/langgraph/retrieval_strategy/planners/retrieval_plan_builder.py`](../../src/application/langgraph/retrieval_strategy/planners/retrieval_plan_builder.py)
- [`src/application/guardrails/context/context_filtering_guardrail.py`](../../src/application/guardrails/context/context_filtering_guardrail.py)
- [`src/application/langgraph/retrieval_strategy/services/retrieval_evidence_merger.py`](../../src/application/langgraph/retrieval_strategy/services/retrieval_evidence_merger.py)
- the deterministic reranker path in the retrieval infrastructure

## 7. Answer Pollution Root Cause

### What the answer pipeline already does correctly

For maintenance answers, the format policy in [`src/application/services/answer_generation/formatting/answer_format_policy.py`](../../src/application/services/answer_generation/formatting/answer_format_policy.py) already instructs the model to:

- use the heading `Maintenance Tasks`
- keep numbered entries
- include description, interval/frequency, component, and reference
- preserve units and page references
- avoid invented values

So the format-policy layer is already pointing in the right direction.

### Why the answer still gets polluted

#### A. The LLM still receives polluted raw sources

`AnswerGenerationService.generate()` passes only approved chunks into the prompt, but those approved chunks can already contain technical specifications.

`AnswerPromptBuilder.build()` then appends all approved raw sources in `_raw_source_block()`.

That means the model sees maintenance evidence and specification evidence in the same prompt, even when the user asked only for maintenance intervals.

#### B. The prompt still exposes internal IDs

`AnswerPromptBuilder._format_source_block()` and `_format_answer_source_block()` include:

- document IDs
- full section paths

This is not the main maintenance-pollution bug, but it is an unnecessary prompt-level leak of internal identifiers.

#### C. The answer intent analyzer re-introduces specification pressure from context

`AnswerIntentAnalyzer._apply_chunk_content_signal()` in [`src/application/services/answer_generation/intent/answer_intent_analyzer.py`](../../src/application/services/answer_generation/intent/answer_intent_analyzer.py) boosts `SPECIFICATION_SUMMARY` when approved chunks contain technical values.

So even if the user question is clearly maintenance-focused, a polluted retrieved context can re-activate specification-style summarization pressure.

### Root cause summary

The answer generator is being asked to stay maintenance-focused while still being shown off-intent technical-spec evidence. The format policy is good, but the evidence set is too permissive and the answer-intent analyzer still reacts to technical values in that evidence.

### Expected fix direction

- tighten retrieval/context approval first
- add maintenance-specific prompt instructions that explicitly forbid unrelated specs
- stop raw approved spec chunks from influencing maintenance answer intent unless the user explicitly requested specs
- remove internal document IDs from answer-generation prompt sources

Likely touch points:

- [`src/application/prompts/answer_generation/answer_prompt_builder.py`](../../src/application/prompts/answer_generation/answer_prompt_builder.py)
- [`src/application/services/answer_generation/intent/answer_intent_analyzer.py`](../../src/application/services/answer_generation/intent/answer_intent_analyzer.py)
- [`src/application/services/answer_generation/formatting/answer_format_policy.py`](../../src/application/services/answer_generation/formatting/answer_format_policy.py)

## 8. Reflection Weakness Root Cause

### Current deterministic reflection logic

`ReflectionService._deterministic_decision()` currently accepts an answer when:

- answer quality score is above threshold
- evidence quality score is above threshold
- there is no document leakage

It does not explicitly reject:

- unrelated technical specifications in a maintenance answer
- answers broader than the maintenance-interval question
- answers missing interval/frequency structure
- answers grounded only in generic maintenance text but not actual interval evidence

### Why this maintenance answer can still pass

`ReflectionService._score_answer()` is generic. It checks:

- non-empty answer
- overlap with question terms
- citation presence
- conciseness

A polluted answer can still satisfy those generic checks.

### Reflection prompt limitations

`ReflectionPromptBuilder.build()` in [`src/application/langgraph/reflection/prompts/reflection_prompt_builder.py`](../../src/application/langgraph/reflection/prompts/reflection_prompt_builder.py) gives the model:

- approved chunk summaries
- rejected chunk summaries
- citations

But the prompt does not encode strong maintenance-interval-specific rejection criteria. It also includes internal chunk IDs and document IDs that are useful for debugging, but not for semantic answer-quality judgment.

### Safe failure handling

`ReflectAnswerNode._decision_patch()` correctly sets a safe fallback response for `FAIL`, which is good. The weakness is earlier: polluted maintenance answers can still be accepted.

### Root cause summary

Reflection is currently generic and evidence-presence-oriented. It is not intent-strict enough for maintenance interval QA.

### Expected fix direction

- add deterministic maintenance-specific rejection criteria
- require interval/frequency structure for maintenance interval answers
- reject answers that mix specs with maintenance intervals unless the user asked for both
- keep the safe failure override path

Likely touch points:

- [`src/application/langgraph/reflection/services/reflection_service.py`](../../src/application/langgraph/reflection/services/reflection_service.py)
- [`src/application/langgraph/reflection/prompts/reflection_prompt_builder.py`](../../src/application/langgraph/reflection/prompts/reflection_prompt_builder.py)

## 9. Required Fix Plan

### A. Single presentation owner

Files:

- [`src/application/agent_runtime/demo_agent.py`](../../src/application/agent_runtime/demo_agent.py)
- [`scripts/demo_agent_cli.py`](../../scripts/demo_agent_cli.py)
- [`src/application/agent_runtime/presenters/console_presenter.py`](../../src/application/agent_runtime/presenters/console_presenter.py)

Planned change:

- keep live `Agent Loop` in normal interactive mode
- suppress post-run `Agent Trace` unless debug/export mode explicitly asks for it

### B. Complete live `Retrieve` and `Observation`

Files:

- [`src/application/langgraph/nodes/question_answering/answer_question_node.py`](../../src/application/langgraph/nodes/question_answering/answer_question_node.py)
- [`src/application/agent_runtime/streaming/event_stream_adapter.py`](../../src/application/agent_runtime/streaming/event_stream_adapter.py)
- [`src/application/agent_runtime/streaming/console_event_sink.py`](../../src/application/agent_runtime/streaming/console_event_sink.py)

Planned change:

- surface explicit retrieval-step metadata for the `answer_question` route
- build live retrieve/observation events from QA retrieval state rather than waiting for a separate graph node that does not exist

### C. Strategy correction for maintenance interval queries

Files:

- [`src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py`](../../src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py)
- [`src/application/workflows/retrieval/retrieval_query_chunk_type_preference_mapper.py`](../../src/application/workflows/retrieval/retrieval_query_chunk_type_preference_mapper.py)
- [`src/application/langgraph/retrieval_strategy/selectors/deterministic_strategy_selector.py`](../../src/application/langgraph/retrieval_strategy/selectors/deterministic_strategy_selector.py)

Planned change:

- remove accidental specification triggers like `" a"` and `" v"`
- treat maintenance interval wording as `MAINTENANCE_LOOKUP` plus `TABLE_LOOKUP`
- allow `PROCEDURE_LOOKUP` only when the wording is procedural
- do not include `TECHNICAL_SPECIFICATION` unless the query explicitly asks for specs

### D. Evidence filtering for maintenance interval QA

Files:

- [`src/application/guardrails/context/context_filtering_guardrail.py`](../../src/application/guardrails/context/context_filtering_guardrail.py)
- [`src/application/langgraph/retrieval_strategy/services/retrieval_evidence_merger.py`](../../src/application/langgraph/retrieval_strategy/services/retrieval_evidence_merger.py)
- retrieval reranker path

Planned change:

- add intent-aware rejection or downgrade for technical-spec chunks in maintenance interval answers
- keep direct maintenance tables and maintenance interval chunks high priority

### E. Prompt and answer generation tightening

Files:

- [`src/application/prompts/answer_generation/answer_prompt_builder.py`](../../src/application/prompts/answer_generation/answer_prompt_builder.py)
- [`src/application/services/answer_generation/intent/answer_intent_analyzer.py`](../../src/application/services/answer_generation/intent/answer_intent_analyzer.py)
- [`src/application/services/answer_generation/formatting/answer_format_policy.py`](../../src/application/services/answer_generation/formatting/answer_format_policy.py)

Planned change:

- explicitly forbid unrelated specs in maintenance-interval prompts
- reduce specification promotion from approved maintenance context
- remove internal document IDs from prompt source blocks

### F. Reflection hardening

Files:

- [`src/application/langgraph/reflection/services/reflection_service.py`](../../src/application/langgraph/reflection/services/reflection_service.py)
- [`src/application/langgraph/reflection/prompts/reflection_prompt_builder.py`](../../src/application/langgraph/reflection/prompts/reflection_prompt_builder.py)

Planned change:

- reject maintenance answers that mix interval evidence with unrelated specs
- require references and interval/frequency structure
- preserve safe failure behavior so stale or polluted answers do not survive

### G. Advisor rejection explanation

Files:

- [`src/application/agent_runtime/react_loop/react_trace_builder.py`](../../src/application/agent_runtime/react_loop/react_trace_builder.py)
- route/request strategy result formatting path

Planned change:

- surface advisor rejection reason directly
- show why deterministic routing/strategy was retained
- make the user-facing trace explain rejection instead of only showing status and event names

## Audit Verdict

The failing maintenance-interval path is not a single bug. It is a chain issue:

1. interactive rendering has two owners
2. retrieval events are hidden inside `answer_question`
3. deterministic strategy selection contains a real false-positive specification trigger
4. maintenance queries currently permit spec chunk types too early
5. context guardrails do not remove off-intent spec evidence
6. answer generation sees the polluted evidence
7. reflection is not strict enough to reject the polluted result

The most concrete and highest-confidence code defect found in this audit is the specification signal extractor matching ordinary English through `" a"` and `" v"` in `_SPECIFICATION_TERMS`, combined with maintenance chunk-type preferences still allowing `ChunkType.TECHNICAL_SPECIFICATION`.
