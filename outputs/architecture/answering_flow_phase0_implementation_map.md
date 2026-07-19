# Answering Flow — Phase 0 Implementation Map

Produced against the team proposition's Phase 0 ("map the existing implementation before changing anything").
Every line below is verified by reading the actual current source — no paraphrasing from memory. Where a call
site was not fully re-verified, it's flagged explicitly rather than assumed.

## Acceptance criterion: trace one `retrieval_qa` question end to end

Example: *"What is the pump maximum flow rate?"*

```
CLI (agent_cli.py / demo_agent_cli.py)
  → AgentRuntime builds initial AgentState via build_agent_state(user_input=...)
  → document_agent_graph.py:184  self._compiled_graph.invoke(initial_state)
  → graph entry edge: START → "route_request"  (document_agent_graph_builder.py:24)

[1] QUERY ENTRY
  RouteRequestNode.__call__()                          route_request_node.py:32
    reads state["user_input"] directly (line 151, via private _route helper)
    → self.intent_router.route(state["user_input"], ...)
    → decision.route_type resolves to RouteType.ANSWER_QUESTION
  → graph routes to AnswerQuestionNode.__call__()       answer_question_node.py:52
    question = state.get("question") or state["user_input"].strip()   (line 76)
    → tool.run(AnswerQuestionRequest(...))                             (line 138)
    tool = ToolRegistry.require("answer_question")

[2] QUERY ANALYSIS / RETRIEVAL INTENT COMPUTED
  QuestionAnsweringWorkflow.run()                       question_answering_workflow.py:152
    route, analyzed_query, analyzed_intent = self._router.decide(question=..., ...)
  → QuestionAnsweringRouter.decide()                    question_answering_router.py:29-55
      builds a raw RetrievalQuery (line 40)
      analyzed = self._query_analyzer.analyze(raw_query)              (line 49)
    → RetrievalQueryAnalyzer.analyze()                  retrieval_query_analyzer.py:42-88
        classification = self.intent_inferer.classify(query)          (line 56)
        query.detected_intent = intent.value                          (line 64)
        query.analyzed = True                                         (line 87)
      ← THIS is where RetrievalQueryIntentInferer.classify() actually runs and
        RetrievalQueryIntentClassification (score/runner_up_score/gap) is produced
      intent = self._query_analyzer.intent_inferer.resolve(analyzed)  (line 50)
      ← .resolve() now just reads the cached detected_intent back out (analyzed=True),
        it does NOT reclassify

[3] RETRIEVAL
  QuestionAnsweringWorkflow._handle_retrieval()         question_answering_workflow.py:222
    self._retrieval_workflow.run(analyzed_query)
  → RetrievalWorkflow.run()                             retrieval_workflow.py:106,111
      query if query.analyzed else self.query_analyzer.analyze(query)   -- SKIPPED, already analyzed
      self.query_analyzer.intent_inferer.resolve(working_query)         -- cache read again, moot
    → executes dense/keyword/hybrid retrieval, returns RetrievalWorkflowResult (chunks + scores)

  [RETRIEVAL STRATEGY — separate, gated, verified NOT on the default path]
  DeterministicStrategySelector.select()                deterministic_strategy_selector.py:33
  RetrievalStrategyService.select_and_plan()            retrieval_strategy_service.py:68-181
    called from AnswerQuestionNode.__call__() line 111, but gated at lines 89-94 on:
      state.get("retrieval_strategy_enabled") and self.retrieval_strategy_policy.enabled
        and self.retrieval_strategy_service is not None and self.retrieval_plan_executor is not None
    build_agent_state() defaults retrieval_strategy_enabled=False (agent_state.py:125)
    → FOR A DEFAULT-CONFIGURATION REQUEST, THIS ENTIRE BRANCH DOES NOT RUN.
      Retrieval happens purely through step [3]'s QuestionAnsweringWorkflow/RetrievalWorkflow chain;
      strategy_patch stays {}.

[4] ANSWER INTENT COMPUTED (up to twice per request)
  AnswerGenerationPipeline.run()                        answer_generation_pipeline.py:196-205,230,232
    join_result = self._structured_fact_joiner.join(...)
  → StructuredFactJoiner.join()                         structured_fact_joiner.py:62-193
      IF resolved_identifiers or resolved_structured_entities are non-empty:
        _resolve_structured_answer_intent_decision()                  (line 130)
          → self._answer_intent_analyzer.analyze(question=..., retrieval_intent=
            analyzed_query.detected_intent, ...)                       (line 193)
          ← AnswerIntentAnalyzer.analyze() call #1 (conditional)
        AnswerContextOrganizer.organize(answer_intent=intent_decision.intent, ...)  (line 136)
          -- runs AFTER and USING the result of call #1, does not call the analyzer itself
      ELSE: intent_decision stays None
    intent_decision = join_result.intent_decision
    gen_request = AnswerGenerationRequest(..., answer_intent_decision=intent_decision)
    generated = self._answer_generation_service.generate(gen_request)

  → AnswerGenerationService.generate()                  answer_generation_service.py:157
      resolved_request, intent_decision = self.request_resolver.resolve(request)
    → AnswerGenerationRequestResolver.resolve()          answer_generation_request_resolver.py:34
        _resolve_intent_decision():                                    (lines 70-93)
          if request.answer_intent_decision is not None: return it     -- reuse call #1's result
          else: return self.answer_intent_analyzer.analyze(...)        -- AnswerIntentAnalyzer.analyze()
                                                                            call #2 (only if #1 didn't run)

[5] DETERMINISTIC-DISPATCH GATE  (this session's Phase 2 addition)
  AnswerGenerationService.generate()                    answer_generation_service.py (~173-183)
    dispatch_gate_decision = self.deterministic_dispatch_gate.evaluate(
        question=..., effective_intent=resolved_request.answer_intent, intent_decision=intent_decision)
  → DeterministicDispatchGate.evaluate()                deterministic_dispatch_gate.py
      contested check: intent_decision.intent == effective_intent and intent_decision.is_contested
      compound check: CompoundQuestionDetector.detect(question=..., driving_intent=effective_intent)

[6] RENDERER SELECTED  (only if NOT bypassed)
  DeterministicAnswerRendererDispatcher.render()         deterministic_answer_renderer_dispatcher.py:49
    tries identifier / spare-parts / maintenance-schedule / procedure-steps / troubleshooting /
    key-value-fact-sheet renderers, in that order, first non-None result wins.

[7] LLM FALLBACK ENTERED  (if bypassed, or no renderer fired)
  AnswerPromptBuilder.build_with_context()               answer_prompt_builder.py
    (PromptContextProjector → EvidenceSchemaFormatter → StructuredEvidencePayloadSerializer →
     RawSourceAppendixFormatter → PromptEvidenceCanonicalizer)
  AnswerGenerationPromptExecutor.execute()                answer_generation_prompt_executor.py
    llm_service.generate(prompt, response_schema=..., temperature=..., num_ctx=...)
    -- retries once with a corrective note on schema-validation failure
  AnswerGenerationResponseParser.parse()                  answer_generation_response_parser.py
  AnswerGenerationResultAssembler.build()                 answer_generation_result_assembler.py

  [Guardrails around this step, inside AnswerGenerationPipeline.run()]
  ContextGuardrailChain.run()                             answer_generation_pipeline.py (~83)
  PreGenerationGuardrailService.check()                   answer_generation_pipeline.py (~165)
  post_answer_guardrails via GuardrailRunner.run_all()     answer_generation_pipeline.py (~272)

[8] REFLECTION ENTERED  (only if reflection_enabled -- default False)
  ReflectAnswerNode.__call__()                            reflect_answer_node.py
    retrieval_result = answer_payload.get("retrieval_result") or {}                  (line 74)
    retrieval_query_intent = extract_retrieval_query_intent(retrieval_result)        (line 100)
  → extract_retrieval_query_intent()                      node_utils.py:31-49
      exact path: answer_payload["retrieval_result"]["retrieval_result"]["query"]["detected_intent"]
      (answer_payload itself = state["tool_results"]["answer_question"]["data"])
  → ReflectionService.review()                             reflection_service.py
      EvidenceSufficiencyStrategyRegistry.evaluate()        reflection_service.py:154
      QueryAmbiguityDetector.detect() -- calls .classify() directly, not .resolve()
      DeterministicReflectionDecider.decide()
      ReflectionValidator.validate()
    → ACCEPT / RETRIEVE_AGAIN (loops back, max 1 retry) / CLARIFY / FAIL

[9] FINAL ANSWER RETURNED
  FinalResponseNode.__call__()                            final_response_node.py:32
    response_text = resolve_state_response_text(state) or state.get("response_text") or "Request completed."
    PostResponseGuardrailService.check()                   final_response_node.py:55
      -- can redact/replace response_text (grounding/secret/injection); sets
         response_text_guardrail_replaced so the recovery heuristic below can't undo it
    recovery heuristic (lines 84-96): recovers the raw generated answer if a safe-failure
      sentinel string appears for a legitimate ACCEPT/ACCEPT_WITH_LIMITATIONS reason,
      UNLESS the guardrail itself just replaced it
    returns {"response_text": final_response_text, ...} → AgentState
  → presenters (console / JSON / Markdown / agent_cli) render from AgentState/GraphResult
```

## Implementation map (quick-reference table)

| Transition | Exact function |
|---|---|
| Query enters at | `RouteRequestNode.__call__()` (`route_request_node.py:32`) → `AnswerQuestionNode.__call__()` (`answer_question_node.py:52`) |
| Retrieval intent computed at | `RetrievalQueryAnalyzer.analyze()` (`retrieval_query_analyzer.py:42-88`), called from `QuestionAnsweringRouter.decide()` (`question_answering_router.py:49`) |
| Answer intent computed at | `AnswerIntentAnalyzer.analyze()`, called from `StructuredFactJoiner._resolve_structured_answer_intent_decision()` (`structured_fact_joiner.py:193`) — conditionally — and/or `AnswerGenerationRequestResolver._resolve_intent_decision()` (`answer_generation_request_resolver.py:70-93`) as fallback |
| Intent scores stored in | **Nowhere in `AgentState`** — confirmed by reading the full `TypedDict` (`agent_state.py:6-106`). Transient Python objects only (`RetrievalQueryIntentClassification`, `AnswerIntentDecision`), passed directly between function calls; only the resolved intent's *string value* survives serialization into `tool_results["answer_question"]["data"][...]["detected_intent"]` |
| Retrieval strategy selected at | `DeterministicStrategySelector.select()` via `RetrievalStrategyService.select_and_plan()` (`retrieval_strategy_service.py:68-181`) — **gated behind `state["retrieval_strategy_enabled"]`, which defaults `False`; does not run for a default-configuration request** |
| Evidence sufficiency evaluated at | `EvidenceSufficiencyStrategyRegistry.evaluate()`, called from `ReflectionService.review()` (`reflection_service.py:154`) — only reached if reflection is enabled |
| Renderer selected at | `DeterministicAnswerRendererDispatcher.render()` (`deterministic_answer_renderer_dispatcher.py:49`), gated by `DeterministicDispatchGate.evaluate()` |
| LLM fallback entered at | `AnswerPromptBuilder.build_with_context()` → `AnswerGenerationPromptExecutor.execute()`, inside `AnswerGenerationService.generate()` |
| Reflection entered at | `ReflectAnswerNode.__call__()` (`reflect_answer_node.py`) → `ReflectionService.review()` |
| Guardrails executed at | `ContextGuardrailChain.run()` / `PreGenerationGuardrailService.check()` / `GuardrailRunner.run_all()` (all inside `answer_generation_pipeline.py`), and `PostResponseGuardrailService.check()` inside `FinalResponseNode.__call__()` (`final_response_node.py:55`) |
| Final answer returned at | `FinalResponseNode.__call__()` (`final_response_node.py:32-115`) |

## Two findings this mapping exercise surfaced (matters for Phase 1+)

1. **`AgentState` has zero fields for intent confidence/margin/scores.** The proposition's "one shared
   decision record in workflow state" doesn't exist today in any form — it would be new state, not a
   refactor of existing state. Both `RetrievalQueryIntentClassification` and `AnswerIntentDecision` currently
   live and die within a single node's function-call chain.
2. **`AnswerIntentAnalyzer.analyze()` can run twice per request** — once inside `StructuredFactJoiner.join()`
   (only when identifiers/structured entities were resolved) and once inside
   `AnswerGenerationRequestResolver` as a fallback when the first didn't run. They can't disagree with each
   other in practice (the resolver reuses call #1's result when it exists), but this is worth knowing before
   building a "canonical dispatch decision" — there is already a de-duplication mechanism for the answer-side
   intent, just not a persisted one.
3. **Retrieval-strategy selection (`DeterministicStrategySelector`) is opt-in and off by default** —
   `retrieval_qa` requests today retrieve purely through `QuestionAnsweringWorkflow`/`RetrievalWorkflow`,
   not through the strategy-selection machinery this session's Phase 2 work (`DeterministicDispatchGate`) sits
   downstream of on the *answer* side. The two "intent classification → downstream decision" paths
   (retrieval-strategy selection vs. answer-dispatch gating) are structurally parallel but not the same
   pipeline for a default request.

## Not fully re-verified (flagged, not assumed)

- `extract_retrieval_query_intent()`'s call site inside `retry_retrieval_node.py` was located by import grep
  but not read in full for this pass — worth confirming before relying on it for the retry-path trace
  specifically.
