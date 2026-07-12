# Per-Category Presentation Status Report

## Executive Summary

The current answer-presentation path is now materially closer to enterprise standard.

Before this upgrade, most answer categories still collapsed into one generic presentation path, spare-parts output was still an ad hoc text block, and console/markdown/JSON did not all resolve the final usable answer consistently.

After this upgrade:

- deterministic category renderers are active for identifiers, spare parts, maintenance schedules, procedure steps, troubleshooting, and structured fact sheets
- render provenance is surfaced through LangGraph result building into the presenters
- console headings now adapt by category/provenance
- safety answers get explicit visual emphasis
- console, markdown, and JSON now use one shared final-answer resolution rule
- spare-parts answers now render as real ASCII tables instead of loose `field: value` lines
- spare-parts reflection validation understands the richer table output

For the CLI answer surface specifically, this is now enterprise-credible rather than debug-like.

## What Was Audited

The audit compared the live codebase against the historical investigation plan in:

- [per_category_presentation_investigation_and_upgrade_plan.md](/abs/path/C:/Users/ashuf/Desktop/Projects/document-ai-assistant/outputs/architecture/per_category_presentation_investigation_and_upgrade_plan.md)

The live code review focused on:

- `src/application/services/answer_generation/answer_generation_service.py`
- `src/application/services/answer_generation/formatting/renderers/`
- `src/application/langgraph/graphs/document_agent/document_agent_answer_extractor.py`
- `src/application/langgraph/graphs/document_agent/document_agent_result_builder.py`
- `src/application/langgraph/common/render_provenance.py`
- `src/application/agent_runtime/presenters/console/graph_result_renderer.py`
- `src/application/agent_runtime/presenters/markdown_presenter.py`
- `src/application/agent_runtime/presenters/json_presenter.py`
- `src/application/langgraph/reflection/detectors/spare_parts_list_context_detector.py`

## Gaps That Existed Before This Pass

### 1. Presenter answer selection was inconsistent

The console had specialized logic to avoid showing the safe failure message for usable reflection outcomes, but markdown and JSON still selected `data["answer"]` / `response_text` directly.

That meant the same graph result could render differently depending on presenter.

### 2. Spare-parts output was not enterprise-grade

`SparePartsListRenderer` still emitted section blocks followed by line-by-line `field: value` rows.

That was readable, but it was not consistent with the newer structured renderers and did not meet the same table-quality bar as maintenance schedules or fact sheets.

### 3. Reflection spare-parts validation was coupled to the old format

The spare-parts legitimacy detector mainly looked for legacy row labels such as `Part No.:`.

Once spare-parts answers moved to a real table, reflection needed to recognize that table as grounded structured evidence rather than misclassifying it.

### 4. One workflow test still assumed all procedure-like answers must hit the LLM

After the deterministic procedure renderer was introduced, a prompt-preservation test still used a pure procedural question and therefore no longer exercised the intended LLM path.

## Implemented Changes

### Shared presenter answer resolution

Added:

- [final_answer_resolver.py](/abs/path/C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/agent_runtime/presenters/final_answer_resolver.py)

This now gives console, markdown, and JSON one shared answer-selection rule:

- preserve guardrail replacements when they are intentional
- recover the generated grounded answer for `ACCEPT` / `ACCEPT_WITH_LIMITATIONS` when the current `response_text` is only the safe failure fallback
- remain backward-compatible with older `GraphResult.data["answer"]`-only test shapes

Updated callers:

- [graph_result_renderer.py](/abs/path/C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/agent_runtime/presenters/console/graph_result_renderer.py)
- [markdown_presenter.py](/abs/path/C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/agent_runtime/presenters/markdown_presenter.py)
- [json_presenter.py](/abs/path/C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/agent_runtime/presenters/json_presenter.py)

### Spare-parts table rendering upgrade

Upgraded:

- [spare_parts_list_renderer.py](/abs/path/C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/services/answer_generation/formatting/spare_parts_list_renderer.py)

The renderer now uses the shared ASCII table utility:

- [ascii_table_renderer.py](/abs/path/C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/shared/text/ascii_table_renderer.py)

Behavioral improvements:

- rows are rendered in aligned columns
- visible columns are selected dynamically from actual row content
- structured-entity spare parts and parsed table rows now share one cleaner output shape
- raw unparsed rows and partial-content notices are still preserved

### Reflection compatibility for structured spare-parts tables

Updated:

- [spare_parts_list_context_detector.py](/abs/path/C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/reflection/detectors/spare_parts_list_context_detector.py)

It now recognizes:

- genuine ASCII-grid spare-parts answers as legitimate grounded evidence
- quantity-only artifact grids as still invalid/incomplete

This preserved the safety of reflection validation while allowing better presentation.

### Test alignment for deterministic procedure rendering

Updated:

- [\_test_question_answering_workflow_part10.py](/abs/path/C:/Users/ashuf/Desktop/Projects/document-ai-assistant/tests/unit/application/workflows/question_answering/_test_question_answering_workflow_part10.py)

The prompt-topology test now uses a narrative maintenance-context question so it continues validating the LLM prompt path instead of being correctly intercepted by the deterministic procedure renderer.

## Current Enterprise-Standard Assessment

### What is now strong

- Category-aware answer rendering is real, not just prompt-instruction text.
- Provenance is visible to the operator.
- Safety answers are visually distinguished.
- Structured categories now look structurally different from generic prose.
- Presenter behavior is consistent across console, markdown, and JSON.
- Spare-parts answers now look like structured tables instead of parser/debug output.
- Reflection logic still protects against fake partial spare-parts answers.

### What is still future enhancement, not an active gap

- A richer UI layer could eventually render true visual tables/cards instead of ASCII tables, but for the CLI this is acceptable and professional.
- Markdown output still mirrors the CLI-oriented text result rather than re-rendering category-specific tables as markdown-native tables. That is a polish opportunity, not a correctness problem.
- There is still room for category-specific export/report templates if the product later grows a web UI or reporting UI, but the CLI path itself no longer looks like raw internal output.

## Validation

Focused suites passed:

- `tests/unit/application/services/answer_generation -q`
- `tests/unit/application/agent_runtime -q`
- `tests/unit/application/langgraph/graphs/test_render_provenance.py -q`
- spare-parts renderer / reflection focused suites

Full suite passed:

```powershell
& 'C:\Users\ashuf\miniconda3\envs\ai-agent-gpu\python.exe' -m pytest -q --basetemp tmp_pytest_presentation_full_03
```

## Verdict

For the CLI answer-presentation layer, the system now meets a practical enterprise standard:

- answers are category-aware
- structured evidence is surfaced as structured output
- provenance is visible
- safety and grounded-answer handling are clearer
- the presentation stack is internally consistent

The remaining work is polish and product evolution, not core answer-presentation hardening.
