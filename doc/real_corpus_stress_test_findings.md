# Real-Corpus Stress Test Findings

Source: `C:\Users\ashu\OneDrive - dintegra\David (shared)'s files - FLW - MY Boardwalk (117m)\Fluegge Delivery Documentation\Approved Documentation` — a real, complete shipyard delivery-documentation corpus (Lürssen Hull 13797), 4642 PDFs + ~400 other files (DWG/JPG/XLSX/etc.), 12.46 GB, spanning dozens of independent suppliers.

Goal: exercise this codebase's actual ingestion pipeline (not ad-hoc scripts) against real documents at scale, to surface concrete weaknesses rather than theoretical ones. This is a different kind of finding from `doc/corpus_confirmation_needed.md` — these are reproduced bugs in the pipeline itself, found by running real files through `scripts/ingest_document.py` and `runtime.parsing_workflow.parse()` directly.

No LLM (Ollama) is available in this environment, so full end-to-end ingestion (classification, extraction) could not be exercised — findings below are scoped to what's testable: Docling parsing, canonical normalization, document graph building, and chunking. That said, two of the findings are about the classification/registration stages themselves, discovered incidentally while probing why a run failed.

---

## 1. SEVERE — Docling's parsing timeout does not reliably bound wall-clock time (GIL starvation)

**What happened:** A real 167-page document (`33111000_22251302-01-310-201_R18.pdf`, Besecke electrical documentation) was configured with a 600-second Docling conversion timeout (`DoclingParser.timeout_seconds`). It actually ran for **1471 seconds** (2.45x over) before the timeout was detected and raised.

To rule out a bug specific to that one call site, I implemented an independent, identically-structured timeout harness around `ParsingWorkflow.parse()` itself (same pattern: daemon thread + `.join(timeout=N)` + check `is_alive()`), set to 120 seconds. On a different real document (`2011298-zipwake_series_s_operators_manual.pdf`, 28 pages), **that timeout also failed** — the call ran for **4702 seconds (78 minutes)** before finally being detected.

**Root cause:** `src/infrastructure/parsing/docling/docling_parser.py::_convert_with_timeout` (lines 90-123) uses `threading.Thread` + `worker.join(timeout=self.timeout_seconds)`, then checks `worker.is_alive()`. This is a reasonable-looking, deliberately-commented pattern (the comment even explains why a daemon thread was chosen over `ThreadPoolExecutor`, to avoid an atexit hang). The problem is structural, not a typo: **a thread-based timeout can only interrupt the *calling* thread's wait — it cannot stop the background thread's actual work.** If that background thread is doing CPU-bound work that holds Python's GIL near-continuously (typical for deep-learning model inference — Docling's layout/table-structure models, especially over many small per-cell/per-region operations), the *main* thread can be starved of the GIL and unable to get scheduled to even check `is_alive()` and raise, for far longer than the configured timeout. The timeout value becomes a lower bound on wait time, not an upper bound.

**Reproduced twice, independently, at two different call sites and two different timeout values (600s→1471s, 120s→4702s) — this is not a fluke of one specific document.**

**Impact:** this is a genuine availability/reliability risk for a production ingestion service, not a cosmetic issue. A single unusually complex real-world PDF (and this corpus, sampled essentially at random, produced two of them in under 40 files tested) can hang ingestion for 10s of minutes to well over an hour, far past its configured "safety" timeout, with no way to recover except killing the whole process externally. At corpus scale (this shipyard corpus alone has ~4600 PDFs), this makes unattended batch ingestion fundamentally unsafe as currently implemented — a small number of pathological documents can each cost an hour-plus of wall-clock time with zero automatic recovery.

**What it would take to fix:** the timeout needs to be enforced at the OS-process level, not the thread level, since only process termination can actually interrupt CPU-bound/GIL-holding native or model-inference code. Concretely: run the Docling conversion in a subprocess (`multiprocessing.Process` with `.terminate()` after a `.join(timeout=N)` that times out, or `subprocess.run(..., timeout=N)` against a small worker script), not a thread. This is a real, non-trivial change (process boundaries mean the `RawParsedDocument`/converter result needs to cross a process boundary via serialization, and Docling's converter object itself may not be cheaply constructible per-subprocess-call without re-loading models each time — likely needs a long-lived worker process pool, not a fresh subprocess per file).

**Question for you:** is this worth prioritizing as its own fix? It's a genuinely serious, reproduced bug, but fixing it properly (process-pool-based timeout enforcement) is real engineering work, not a one-line change.

**Update — this isn't confined to large documents, and it's worse than the above makes it sound.** A follow-up pilot batch (intended as "smallest files first," but due to a bug in my own harness — I sliced to a fixed count *before* sorting by page count, against a list that was itself originally sorted largest-first — actually sampled a cluster of documents that all happened to be exactly 28 pages) produced this before I stopped it:

| File | Pages | Result |
|---|---|---|
| `FLW_MY13797_FD_Security_System_ASBUILT_PREA.pdf` | 28 | Timeout at 120.02s (harness limit — true duration unknown, could be much longer) |
| `Vetus WCPS12 (85098000).pdf` | 28 | Success in 115.12s (137 sections, 1025 elements, 162 chunks, 17 tables, 66 pictures) |
| `Sea-Fire NFD-NFG Manual.pdf` | 28 | Timeout at 120.02s |
| `Marinco_Inverter_Manual.pdf` | 28 | Timeout at 120.02s |
| `2011298-zipwake_series_s_operators_manual.pdf` | 28 | Timeout at 4702.47s (78 minutes) |

**4 of 5 real, unremarkable 28-page vendor equipment manuals (toilet, fire suppression, inverter, trim tabs — the kind of image/diagram-heavy scanned manual that's extremely common in real supplier documentation) either hung or took over 2 minutes.** Only one finished, and it took 115 seconds — barely under the harness limit. This means the timeout/hang risk isn't a large-document (200+ page) problem, it's a **routine, everyday-real-document** problem. A representative real-world ingestion batch could plausibly see this class of failure on a large fraction of files, not just outliers.

---

## 2. Exception-handler failure-recording path itself crashes on an FK violation, masking the real error

**What happened:** Re-ingesting an already-registered document via `--force` failed with an unhelpful `DatabaseError: Failed to commit database transaction.` — no indication of what actually went wrong.

**Root cause, traced via direct reproduction with a monkeypatched exception handler:**
1. The real, original failure was `sqlite3.IntegrityError: UNIQUE constraint failed: documents.file_hash` — a duplicate `file_hash` INSERT attempt (this specific document had already been registered by an earlier test run of mine; `--force` bypasses the *duplicate check* step but doesn't handle the resulting DB-level conflict gracefully).
2. `src/application/workflows/ingestion/pipeline/outcome/ingestion_exception_handler.py::handle()` catches this, calls `self.run_store.rollback()` (correctly undoing the failed document insert), then tries to `self.run_store.update(ingestion_run)` to record the failure — **but `ingestion_run.document_id` was already set to the document ID that the rollback just erased.** `ingestion_runs.document_id` is a real `SET NULL` foreign key (added earlier this session as part of the CASCADE/`ondelete=` migration work) to `documents.id`. Setting it to a document ID that doesn't exist violates the FK constraint, so *this* UPDATE also fails — with a second, unrelated `IntegrityError`, which is what actually surfaces to the caller. The original, informative exception is discarded entirely; only `str(exc)` for the *second* failure reaches the user.
3. Separately: even without the FK crash, `IngestionExceptionHandler.handle()` never logs a full traceback anywhere (no `logger.exception(...)` call) — only `str(exc)`. Diagnosing ingestion failures from logs alone would already be hard even if the FK bug weren't there.

**Impact:** any ingestion failure that occurs after a document row is tentatively created but before the transaction commits (which — per finding #1 above — is now a code path that's actually reachable in normal operation, not just a `--force` edge case) will crash the failure-recording path too, permanently hiding the real error behind a generic, unhelpful message. This makes any real ingestion failure much harder to diagnose than it should be.

**What it would take to fix:** `IngestionExceptionHandler.handle()` should not blindly reuse `ingestion_run.document_id` when recording a failure if the underlying document write didn't survive the rollback — either clear it defensively before the failure-record update, or record the failure via a path that doesn't re-trigger the same FK. Separately, adding a `logger.exception(...)` call (with the *original* exception, before any secondary failure) would make this whole class of bug far easier to diagnose in the future.

---

## 3. `CLASSIFICATION_ENABLED` and `CLASSIFICATION_USE_LLM` are dead settings — no code reads them

**What happened:** with both set to `false`/`true` respectively in `.env` (as they already were), a real ingestion run still attempted to call the classification LLM (and failed, since no Ollama is available here).

**Confirmed via exhaustive grep across `src/`:** `classification_settings.enabled` (backing `CLASSIFICATION_ENABLED`) and `classification_settings.use_llm` (backing `CLASSIFICATION_USE_LLM`) have **zero consumers anywhere in the codebase** — not in the classification workflow, not in orchestrator wiring, nowhere. They're defined as `Field`s on `ClassificationSettings`, documented in `.env`/`.env.example`, and then never read again. Setting either has no effect on runtime behavior whatsoever; the classification LLM call runs unconditionally regardless.

**Impact:** this is a real operability gap. Anyone trying to run this pipeline without an LLM available (exactly this environment's situation) has no documented, working way to disable classification — the settings that look like they should do exactly that are vestigial.

**What it would take to fix:** either wire `classification_settings.enabled` into the actual gate that decides whether the classification stage runs at all (likely in the ingestion orchestrator or `ClassificationService`), or remove the dead settings entirely if they're truly obsolete — leaving them in place, unused, is actively misleading.

---

## 4. Corpus inventory — composition of a real 4642-file shipyard corpus

For calibrating future testing/sampling decisions:

| Page count | File count | % |
|---|---|---|
| 1 page | 2253 | 48.5% |
| 2-10 pages | 1457 | 31.4% |
| 11-50 pages | 601 | 12.9% |
| 51-200 pages | 266 | 5.7% |
| 201-1000 pages | 58 | 1.25% |
| 1000+ pages | 5 | 0.1% |

- 80% of real documents in this corpus are ≤10 pages (mostly individual CAD drawings/certificates, consistent with the `Batch_D` findings in `corpus_confirmation_needed.md`).
- The long tail is real and significant: 63 documents exceed 200 pages, up to **4130 pages** (`31197706_Final documentation.pdf`, already analyzed) and **3405 pages** (`4670 Heinen&Hopmann MAN HVAC.pdf`, not yet examined).
- **2 files are outright corrupt/unreadable** (PDFium: "Data format error") — a real, if small, class of failure the pipeline needs to handle gracefully (both are electrical schematic sheets from the same `12m BeachLander`/`12m Limo` sub-project, suggesting a shared export/corruption issue at the source, not random).
- Given finding #1 above, the 63 large documents (and likely a nontrivial fraction of the 51-200 page tier too, based on the two pathological cases already found) cannot be safely batch-processed unattended until the timeout mechanism is fixed — each one is a real risk of an hour-plus unrecoverable hang.

**Not yet done, pending your direction given finding #1:** a full parsing-only stress test across the ≤30-page bulk of this corpus (~4300+ files) was planned but paused after finding #1 — and the small sample already gathered there (see the finding #1 update above: 4 of 5 real 28-page documents hung or exceeded 2 minutes) suggests this isn't a rare edge case confined to huge documents; it may affect a large fraction of ordinary real documents. I'd want either a process-based timeout harness (see finding #1) or your explicit sign-off on accepting long unattended run times before resuming a large batch run.

---

## Suggested next step

Finding #1 is the one that actually blocks doing more of what you originally asked (a full-corpus sweep) safely — it's not just a finding, it's the reason I paused rather than continuing to burn hours on an approach already shown to hang unpredictably, and the follow-up data point (4 of 5 ordinary 28-page manuals hanging or running slow) means it's likely to bite often, not rarely. I'd suggest deciding on #1 first — either invest in a proper process-based timeout fix before attempting any real large-scale ingestion of this corpus, or explicitly accept the risk and let me continue with much closer supervision and short, small batches rather than a large unattended run. Treat #2/#3 as smaller, independent fixes you can slot in whenever.
