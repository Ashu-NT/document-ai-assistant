# ACCEPT_WITH_LIMITATIONS Final Response Bug

## 1. Goal

Debug why a maintenance interval question can end with:

`Reflection = ACCEPT_WITH_LIMITATIONS`

but still display:

`I could not verify a grounded answer confidently enough from the current evidence.`

instead of the best grounded generated answer.

## 2. Relevant Runtime Path

Active path for a reflected QA request:

1. `answer_question` node builds/generated answer payload
   File: [src/application/langgraph/nodes/question_answering/answer_question_node.py](../../src/application/langgraph/nodes/question_answering/answer_question_node.py)
2. `reflect_answer` node runs reflection review
   File: [src/application/langgraph/nodes/question_answering/reflect_answer_node.py](../../src/application/langgraph/nodes/question_answering/reflect_answer_node.py)
3. `final_response` node resolves final text and runs post-response guardrail
   File: [src/application/langgraph/nodes/control/final_response_node.py](../../src/application/langgraph/nodes/control/final_response_node.py)
4. `DocumentAgentGraph._build_result()` builds `GraphResult`
   File: [src/application/langgraph/graphs/document_agent_graph.py](../../src/application/langgraph/graphs/document_agent_graph.py)
5. `ConsolePresenter.render_graph_result()` prints the final answer
   File: [src/application/agent_runtime/presenters/console_presenter.py](../../src/application/agent_runtime/presenters/console_presenter.py)

## 3. Required State Fields and Current Handling

### 3.1 Generated answer before reflection

Source:

- `tool_results["answer_question"]["data"]["answer_text"]`
- fallback used in `ReflectAnswerNode.__call__()`:
  - `answer_payload.get("answer_text")`
  - or `state.get("response_text")`

Code:

- [reflect_answer_node.py](../../src/application/langgraph/nodes/question_answering/reflect_answer_node.py)

Observation:

- Reflection reads the generated answer from the `answer_question` payload correctly.

### 3.2 Reflection decision

Source:

- `result.decision.decision.value`

Stored back into state by `ReflectAnswerNode`:

- `reflection_result`
- `reflection_decision`
- `reflection_score`

Observation:

- `ACCEPT_WITH_LIMITATIONS` is already stored as a normal reflection decision.

### 3.3 Reflection safe failure message

Constant:

- `REFLECTION_SAFE_FAILURE_MESSAGE`
- File: [src/application/langgraph/reflection/constants/reflection_constants.py](../../src/application/langgraph/reflection/constants/reflection_constants.py)

Current text:

- `I could not verify a grounded answer confidently enough from the current evidence.`

### 3.4 `response_text`

Where it is set during reflection:

- `ReflectAnswerNode._decision_patch()`

Current behavior:

- `RETRIEVE_AGAIN`:
  - no `response_text` written
- `CLARIFY`:
  - `response_text = clarification_message`
- `FAIL`:
  - `response_text = REFLECTION_SAFE_FAILURE_MESSAGE`
- `ACCEPT` / `ACCEPT_WITH_LIMITATIONS`:
  - no `response_text` patch is written

Observation:

- `ACCEPT_WITH_LIMITATIONS` itself is not directly treated like `FAIL` in `ReflectAnswerNode`.
- So the bug is likely downstream if stale failure text already exists in `state.response_text`.

### 3.5 `tool_results["answer_question"]["data"]["answer"]`

Actual active answer payload field used by final answer resolution is not `data["answer"]`.

Current resolver looks for:

- `tool_results["answer_question"]["data"]["answer_text"]`
- then `safe_user_message`

Code:

- [response_text_resolver.py](../../src/application/langgraph/common/response_text_resolver.py)

Observation:

- `tool_results["answer_question"]["data"]["answer"]` is not the primary active field in the current resolver.
- If stale `state.response_text` exists, it wins over `answer_text`.

### 3.6 `final_response_node` output

Current logic:

```python
response_text = (
    resolve_state_response_text(state)
    or state.get("response_text")
    or "Request completed."
)
```

Important detail:

- `resolve_state_response_text(state)` prefers `state["response_text"]` first
- only then falls back to `tool_results["answer_question"]["data"]["answer_text"]`
- after that, `FinalResponseNode` runs the post-response guardrail

Observation:

- If `state["response_text"]` already contains `REFLECTION_SAFE_FAILURE_MESSAGE`, the usable generated answer is ignored.
- Even when reflection returns `ACCEPT_WITH_LIMITATIONS`, the post-response guardrail can still replace a usable answer with:
  - `I could not verify a grounded answer confidently enough from the current document evidence.`
- So the real failure path is broader than stale state precedence alone: a safe-failure fallback can still overwrite a usable reflected answer late in the pipeline.

### 3.7 `GraphResult.response_text`

Current logic in `DocumentAgentGraph._build_result()`:

- `answer = _extract_answer(tool_results, state.get("response_text"))`
- success path returns:
  - `response_text = answer or state.get("response_text")`

Important detail:

- `_extract_answer()` delegates to `resolve_answer_text(...)`
- `resolve_answer_text(...)` also prefers `fallback_response_text` first

Observation:

- If `state.response_text` is stale failure text, then:
  - `answer` becomes the failure text
  - `GraphResult.response_text` becomes the failure text
  - `GraphResult.data["answer"]` also becomes the failure text
- If `FinalResponseNode` already accepted a late safe-failure fallback from the post-response guardrail, the same bad value is propagated again here.

This propagates the bad value twice.

### 3.8 `ConsolePresenter` selected final answer

Current display order:

```python
result.response_text or (result.data or {}).get("answer") or ""
```

Observation:

- Presenter is not the root cause.
- It displays the wrong text because both `GraphResult.response_text` and `data["answer"]` can already be polluted upstream by stale failure text.

## 4. Root Cause Summary

The incorrect behavior is not primarily caused by `ReflectAnswerNode`.

The confirmed root cause is a two-step overwrite path:

1. `resolve_state_response_text(state)` prefers `state.response_text`
2. `FinalResponseNode` then runs the post-response guardrail, which can replace a usable grounded answer with its own grounding-failure safe message
3. `DocumentAgentGraph._build_result()` can preserve that safe-failure message again when building `GraphResult`
4. `ConsolePresenter` simply prints the already-corrupted final result

So if a safe failure message appears in `state.response_text`, or the post-response guardrail introduces it late, `ACCEPT_WITH_LIMITATIONS` can still show the failure text unless the pipeline explicitly treats this decision as usable.

## 5. Expected Behavior Matrix

### ACCEPT

- final answer = generated answer

### ACCEPT_WITH_LIMITATIONS

- final answer = generated answer
- footer shows `Reflection : ACCEPT_WITH_LIMITATIONS`
- safe failure message must not be shown

### RETRIEVE_AGAIN

- retry if allowed
- if retry exhausted and useful evidence exists:
  - convert to `ACCEPT_WITH_LIMITATIONS`
- if no useful evidence exists:
  - fail

### CLARIFY

- final answer = clarification question

### FAIL

- final answer = `REFLECTION_SAFE_FAILURE_MESSAGE`

## 6. Required Fix Areas

### A. Final response resolution

Files:

- [src/application/langgraph/common/response_text_resolver.py](../../src/application/langgraph/common/response_text_resolver.py)
- [src/application/langgraph/nodes/control/final_response_node.py](../../src/application/langgraph/nodes/control/final_response_node.py)

Need:

- explicit handling for `reflection_decision == "ACCEPT_WITH_LIMITATIONS"`
- if current `response_text` equals `REFLECTION_SAFE_FAILURE_MESSAGE`, prefer generated answer payload instead
- if the post-response guardrail returns its grounding-failure message, recover the generated answer instead of surfacing a false failure

### B. Graph result assembly

File:

- [src/application/langgraph/graphs/document_agent_graph.py](../../src/application/langgraph/graphs/document_agent_graph.py)

Need:

- `GraphResult.response_text` must preserve usable answer text for `ACCEPT_WITH_LIMITATIONS`
- guard against copying failure text into `data["answer"]`

### C. Presenter safety guard

File:

- [src/application/agent_runtime/presenters/console_presenter.py](../../src/application/agent_runtime/presenters/console_presenter.py)

Need:

- if reflection decision is `ACCEPT_WITH_LIMITATIONS`, do not prefer the safe failure message over a usable answer

### D. Reflection node guard

File:

- [src/application/langgraph/nodes/question_answering/reflect_answer_node.py](../../src/application/langgraph/nodes/question_answering/reflect_answer_node.py)

Need:

- confirm `ACCEPT_WITH_LIMITATIONS` never writes `REFLECTION_SAFE_FAILURE_MESSAGE`
- optionally add defensive reset if stale failure text is already present

## 7. Audit Verdict

`ACCEPT_WITH_LIMITATIONS` is correctly modeled as a usable reflection decision, but the final answer pipeline still had safe-failure precedence.

Most likely fault:

- `resolve_state_response_text()` and `DocumentAgentGraph._build_result()` prefer `state.response_text` too early.
- `FinalResponseNode` also needed a guard against the post-response guardrail replacing a usable answer with a grounding-failure fallback.

That is where `ACCEPT_WITH_LIMITATIONS` is effectively being treated like `FAIL`.
