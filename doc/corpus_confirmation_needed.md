# Open Questions Needing Human/Domain Confirmation

Source corpora explored so far:
- `C:\Users\ashu\Downloads\SupplierDocumentation_I` (594 PDFs, supplier/manufacturer documentation for what appears to be a yacht build — cable plans, manuals, certificates, drawing registers, across ~20 supplier folders).
- `C:\Users\ashu\Downloads\New` (9 PDFs, mixed manuals/drawings, including the maintenance-schedule PDF that triggered discovery #0 below).
- `C:\Users\ashu\Downloads\Documentation_Batch_10` (3 FMD wastewater-system manuals).
- `C:\Users\ashu\Downloads\31197706_Final documentation.pdf` (4130 pages — the complete MAN Energy Solutions main-engine documentation package for Lürssen Hull 13797, 2x 12V 175D-ML engines; effectively dozens of sub-manuals concatenated into one file, with a 12,160-entry PDF bookmark tree).

This covers the three items from `doc/end_to_end_pipeline_audit.md` that were deliberately left unimplemented pending real data (P2 items #12, #14, #15). For each, I've noted what I found in this corpus so far and the specific question(s) only you can answer. Nothing below has been implemented yet — I'll act once you've filled in answers.

---

## 0. NEW discovery, bigger than originally scoped — PDF-native link cross-references

You pointed me at `C:\Users\ashu\Downloads\New\System Manual PB-06175 v0.pdf`, page 313's maintenance schedule table, which has clickable links to referenced procedure pages. I investigated the mechanism directly (via `pypdfium2`, bypassing Docling) and this turned out to be a more significant finding than the drawing-ID text-pattern question below.

**What I found:**

- Page 313's maintenance table has real embedded PDF link annotations — 13 of them — each resolving to an exact destination page index via the PDF's own internal structure (`FPDFLink_GetDest`/`FPDFDest_GetDestPageIndex`), not a text guess.
- I verified the targets are correct: the text says *"See Operating instructions ... on page 41"*, and the link resolves to physical PDF page 49, which really does contain "3 Operating instructions and control system description" with the printed footer page number "41" — confirming the printed page number and the physical PDF page position are offset (front matter — cover, TOC, revision history — pushes real content pages later than their own printed numbering). Same pattern held for "page 344" → physical page 352, and "page 308" → physical page 316 (consistently +8 for these three). Two other links landed at offsets of roughly +6 to +10, so **the offset isn't even a fixed constant across the whole document** — it's not something a page-number-text-parsing approach could safely compute without more work.
- **Docling — the parser this project already uses for ingestion — throws this data away entirely.** I checked both of Docling's PDF backends (`pypdfium2_backend.py`, `pdf_backend.py`, 557 lines combined) for any link/annotation handling: zero mentions. The link data exists in the PDF and is exactly resolvable, but nothing in the current ingestion pipeline captures it.

**Why this matters more than the drawing-ID question below:** the existing audit finding (`chunk_cross_reference_detector.py:25-34`) already says page-based references are the more precise mechanism, but section/chapter references only resolve via *fuzzy title-matching* — lower precision. This corpus shows real documents contain **exact, unambiguous** cross-reference data (PDF link destinations) sitting completely unused. Wiring this in would mean cross-reference resolution for these documents could stop guessing entirely for links that exist, and only fall back to fuzzy text matching where a real link isn't present.

**What it would take:** a real (if scoped) engineering effort, not a quick fix — Docling doesn't expose this, so it needs a separate `pypdfium2`-based extraction pass alongside/before Docling conversion, capturing each page's link annotations (source rectangle + destination page), then correlating a link's source location with whichever element/chunk it falls inside during graph building, then threading "this chunk has a resolved link to page N" through to `ChunkCrossReference` instead of (or alongside) the fuzzy text-based detector.

**Update — this is not a one-off.** I scanned all 8 other PDFs in `Downloads\New` for link density (sampling ~40 pages per doc) and text-based "see page N" / drawing-doc cue phrases (first 30 pages each):

| Document | Pages | Link annots (sampled) | Text cue hits |
|---|---|---|---|
| `EN_Betriebsanleitung.pdf` | 38 | 0 | 1 ("on page N") |
| `TD_28022101_Rev-A.pdf` | 88 | **340**, on **100% of sampled pages** | **0** |
| `002878 - MY Cosmos - Full System Manual...pdf` | 443 | 139 (9/40 pages) | 0 |
| `Z700-700-22_R1.0...pdf` | 118 | 186 (7/40 pages) | 0 |
| `INSTRUCTIONS_LURSSEN_42602 COSMOS.pdf` | 13 | 0 | 0 |
| `KSB_FSD_A3000_E3000mini...pdf` | 54 | 0 | 0 |
| `KSB_FSD_A3000_E3000-L-400...pdf` | 63 | 0 | 0 |
| `14384836_1263514_BA MY COSMOS SRT_en.pdf` | 309 | **433** (18/40 pages) | 0 |

Four of these eight have substantial real link annotations (139-433 sampled) with **zero** text-based cross-reference cues found anywhere. `TD_28022101_Rev-A.pdf` is the extreme case: every single sampled page had links, and there was not one "see page N" or "see drawing/document" phrase in the first 30 pages. For a document like that, a text-only cross-reference detector wouldn't just be less precise than using the links — it would find **nothing at all**. This meaningfully raises my confidence that discovery #0 isn't specific to one well-authored PDF; it looks like a real, recurring authoring pattern across at least this corpus.

**Update 2 — the 4130-page MAN engine documentation confirms it again, at scale.** Sampled 150 pages evenly across the full document: **31 of 150 (~21%) had real PDF link annotations, 664 links total in the sample** (extrapolated, this single document likely has well over 10,000 real link annotations across its full 4130 pages). This is now confirmed across 5 real documents from 3+ different sources/manufacturers — not a one-off.

**Questions for you:**

1. Is this worth pursuing as real engineering work? It's bigger scope than the original "detect a drawing-ID text pattern" item — more like a new capability than a fix. Yes this is very mportant real enginering work and we need to implement it not duplicate creations , scalable, flexible, maintenanble, testable
2. Given this holds up consistently across every large real document sampled so far, does that match your sense of how common this is across the documents you actually work with? This will be common across manuals 
3. If yes to pursuing it — should it fully replace the fuzzy section/chapter matcher wherever a real link exists, or run alongside it as a higher-confidence signal that wins when both fire? it is possible for a document to have both best option is use whichever is found but if both are found on exactly same locations verify if both reference to same chunk/element if they mismatch then we need a better way to resolver maybe a heuristic, forh exaple some link might have like section/chapter 3.1, in cases like this the fuzzy will win  as during parsing will have exactly such numbering
---

## 1. Drawing-ID cross-reference patterns (audit item #12)

**Goal:** teach `chunk_cross_reference_detector.py` to recognize when running text references a specific drawing/document by ID (e.g. "see Drawing SK-1044"), the way it already does for page and section references.

**What I found:**

- Real document-ID convention exists and is concrete: Ideaworks' own register (`3970 0020 ... Documentation Register.pdf`) uses `IDW-D0000`, `IDW-D1000`, `IDW-D2000`, etc. — supplier prefix + `D` + sequential number. This is a real, usable pattern, but it's **this one supplier's own scheme** — other suppliers in the corpus almost certainly use different conventions (I haven't checked their registers yet).
- I scanned the first 12 pages of 60 manuals (`MAN`/`CER`/register/list-type documents) for cue phrases ("see drawing", "refer to document", "as shown in", etc.) near an ID-like token. Only **2 of 60** had any hit at all:
  - `2670 0150 ABB ... System Descriptions.pdf`: *"...information see document: System description of..."* — references a document by **title/description**, not an ID.
  - `2863 0025 KSB ... Butterfly Valves Addition.pdf`: *"(See drawing pag.4)"* — references a **page number**, not a drawing ID.
- Neither real example found so far actually cites a drawing by its ID code in prose. That's a small, early sample (first 12 pages only, 60 of 594 files, one cue-phrase list I wrote myself) — not proof the pattern doesn't exist, just that it's not obviously common.

**Update — the picture has converged, and it points away from the original framing.** I dug into the 4130-page MAN engine documentation (`31197706_Final documentation.pdf`) specifically for this. It has its own real structured document-ID scheme, visible directly in the PDF bookmark tree (e.g. `000.100.005_100204576_001_07_Guideline for Installation`) and page footers (`P010.220.115-01-0002`). Searching 150 sampled pages for that ID shape in running text found 66 hits — but checking the actual context (page 1790) showed they weren't cross-references at all: they were **"Order No." values in a spare-parts catalog table** (`010.220.115-0002-ZVZDR = Lubricating oil centrifuge`, etc.) — structured part numbers in a table, not IDs cited in prose.

Meanwhile, the same 150-page sample found only 4 genuine cross-reference cue-phrase hits, and every one of them was **"see section/chapter TITLE on page N"** — e.g. *"case of engine operation under arctic conditions (see section Engine operation under arctic conditions, Page 75)"*, *"See chapter 3.3 Approved Personnel on page 14"*. That's the exact same phrasing convention found in the original maintenance-schedule PDF and in the one ABB hit from the supplier corpus — now confirmed independently across 3 different manufacturers.

**So the real, evidence-backed picture across everything sampled so far is:** these documents don't cross-reference each other by citing a drawing/document ID in prose (the "see Drawing SK-1044" pattern the original audit speculated about). They cross-reference by **title + explicit page number** — which is exactly what `chunk_cross_reference_detector.py`'s page-reference detection (already flagged in the audit as the *higher-precision, already-working* mechanism) should already substantially handle — while document/part/drawing IDs live in structured tables and registers, not free prose.

**Questions for you:**

1. Does this reframing match your own experience — i.e., is "see X on page N" really the dominant real cross-reference style, with ID-based citations mostly confined to tables/registers rather than prose? If so, the original "detect a drawing-ID text pattern in prose" framing of #12 may not be the right investment — the better one is likely strengthening/validating the *existing* page+title matcher, and (bigger win) discovery #0's PDF-link extraction, since real links resolve these same "page N" references exactly instead of fuzzily. yes we move to strengthening/validating of existing
2. Separately — the spare-parts "Order No." format found on page 1790 (`010.220.115-0002-ZVZDR`) looks like a genuine, structured part-number convention. Is that worth feeding into the *existing* identifier-extraction/part-number-lookup system (a different, already-strong part of the pipeline, per the original audit) as validation/expansion data? Not urgent, just flagging it since I found it. , for this document that is validate, so it can be added to the identifier
3. Do you want me to keep sampling more of the 594-file supplier corpus specifically for counter-examples (real "see Drawing X" prose citations), to make sure I'm not over-generalizing from documents that happen to favor page-based references, or is the evidence gathered so far enough to act on? we keep validating against all docs but not limited to these docs since the system will be used on different documentations not listed here

---

## 2. Maritime jargon / synonym expansion (audit item #14)

**Goal:** give `retrieval_query_rewriter.py` a synonym layer for domain concepts (e.g. generator/genset, valve/cock) beyond the identifier-abbreviation expansion it already has.

**What I found:**

- The "Manufacturer Information A to Ch / Ci / Cr to G / ... T to Z" files (Ideaworks folder) are **not** a glossary or terminology reference — they're large concatenated bundles of raw third-party OEM manuals, organized alphabetically by manufacturer name (e.g. the "A to Ch" file opens with an APC UPS manual). Genuinely useful real technical prose, but not a synonym source.
- **Update — real, authoritative source found in `Documentation_Batch_10`.** All three FMD wastewater-system manuals in this folder (`19P006-33-GTC...`, `19P006-36-BCT...`, `FMD_GS_Manual...`) share a standardized "Definitions" + "Abbreviations" template section, e.g.:
  - Definitions (process-specific, GTC manual): `BW = Black water` (toilets/sickbay wastewater), `DFWL = De-watered food waste liquor`, `FOG = Fat Oil & Grease`, `GW = (accommodation) Grey water`, `GWL = Laundry grey water`, `GWG = Galley grey water` — each with a full explanatory sentence, not just a bare expansion.
  - Abbreviations (shared boilerplate across all three, with per-document extras): `DIN = German Industry Standard`, `DN = Diameter Nominal`, `EN = European Standard`, `ISO = International Organization for Standardization`, `PPE = Personal Protection Equipment`, plus (GTC manual only) `HAT = Harbour Acceptance Test`, `IAS = Integrated Alarm and Monitoring System`, `PP = Pump`, `SBR = Sequencing Batch Reactor`, `VV = Valve`.
  - These are genuinely low-risk to use as-is: they're author-published in the manual itself, not inferred or guessed — there's no ambiguity to validate the way there would be for a synonym pair I mined myself.
- **Update — same pattern found again in the MAN engine documentation**, and this time with genuine conceptual definitions, not just abbreviations: its "1.2 Definitions" section (in an embedded safety-information sub-manual) explains **Diesel-electrical** (engine drives a generator, which powers electric motors driving the propellers), **Diesel-mechanical** (engine drives the propeller directly via transmission/shaft), and **Windmilling** (the propeller drives the main drive, i.e. reverse of normal operation) — full concept explanations, not abbreviation pairs. Its "1.3 Abbreviations" table adds `DE`/`DM`/`GVU`/`HFO`/`HT`/`IMO`/`MARPOL`/`MDO`/`LT`/`PTH`/`SOLAS`/`LEL`/`UPS`/`VVT` to the FMD list found earlier. Still no genuine "generator ↔ genset"-style synonym pair found anywhere yet, but real Definitions/Abbreviations sections now confirmed present in documentation from at least 2 different manufacturers — worth treating as a real, recurring authoring convention in this document genre, not a fluke.
- **Important distinction, though:** most of this is abbreviation *expansion* (BW ↔ Black water), the same category `retrieval_query_rewriter.py` already handles for identifier labels (p/n, dwg no.) — not the conceptual *synonym* pairing the original audit finding was actually about (generator/genset, valve/cock — two full words for the same real-world thing, no abbreviation involved). The MAN document's "Definitions" section is closer to that (full concept explanations), but still isn't a synonym pair per se.

**Questions for you:**

1. Should I go ahead and wire in the abbreviation pairs found above (they're authoritative, from the documents themselves) even though they don't solve the original "conceptual synonym" framing of #14? That seems like a legitimate, safe win on its own. yes we can start with them but design needs to be extensible maybe a config yaml where we can easily just add as we research
2. For the harder problem — real synonym pairs like generator/genset — do you (or anyone on the team) have maritime/shipyard domain expertise to validate candidates? That's the actual blocker: even mining candidates from the corpus via co-occurrence, I have no way to confirm a pairing is right, or catch a wrong one. we do not have one now, what will can do is generate a complete list then outsource it for an engineer to validate the list
3. Is there an existing glossary, style guide, or terminology list anywhere (even outside these folders) that's authoritative for this project? No
4. Should I keep scanning the other suppliers in `SupplierDocumentation_I` for similar Definitions/Abbreviations sections (now that I know the pattern to look for), or is what's already found from FMD enough to act on for now? We can extend as neccessary

---

## 3. Reranker weight validation (audit item #15)

**Goal:** validate/tune `deterministic_hybrid_reranker.py`'s hand-picked scoring weights against real relevance judgments.

**What I found:** Nothing — and nothing in this corpus *can* help with this one. This corpus is source documents only; it has no queries and no relevance judgments attached to it.

**Question for you:**

1. Do you have (or can you produce) a set of real questions that have actually been asked against documents like these, along with which chunk/passage was the correct answer for each? That's the only thing that unlocks this item — a bigger or different document corpus doesn't help. You can generate then i will confirm
2. If that doesn't exist yet, would you want to hand-build a small golden set (e.g. 20-30 realistic questions against a subset of this corpus, each with the correct answer marked) once these documents are actually ingested? That's a real, if smaller, path to unblocking this item. yes maybe  500 real questions

---

## Suggested next step

Once you've answered what you can above, tell me and I'll pick back up. Of everything found so far, two things look ready to act on without waiting on anything further: wiring in the FMD/MAN abbreviation and definition pairs (item #14, question 1) and — pending your answer on priority/scope — discovery #0's PDF-link extraction, now backed by evidence across 5 real documents from 3+ manufacturers, including a 4130-page document with an estimated 10,000+ real link annotations. Item #12 as originally framed ("detect a drawing-ID text pattern") looks, on the evidence gathered so far, like it may be solving a problem these real documents don't actually have — see the updated recommendation in section 1 above.
