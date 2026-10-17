# Public runner protocol

The private aggregate calibration and the fictional public runs are separate experiments.
This standalone runner was newly authored; it is not the frozen original private implementation.

Events contain id, scope, timezone-aware at, origin and text. Cases contain id, q, gold JSON fields,
evidence IDs and optional scope/forbidden_markers. The evaluator owns gold; adapters receive only
source events or question+scope, and the answer model sees only question+packed context.

Input order must be chronological; sources newer than query time are rejected. The producer must
still ensure an old-looking summary was not computed from future messages. This is not a full
bitemporal replay implementation. The manifest binds inputs, model, source code and key configuration;
new settings need a new output directory. A file lock prevents concurrent local writers. Pending
native writes are not silently resubmitted after a lost acknowledgement. This is not exactly-once
execution. Read-only means no source re-ingestion; graph initialization can still set up indexes.

RAG uses 240-token chunks, stride 200, Unicode-word BM25 and cosine similarity with RRF, top 12.
Mem0 uses inferred facts, top 12 and threshold 0. Graphiti uses native edge search or a separate
combined RRF profile interleaving episodes, edges and entities. No custom ontology is supplied.
Hindsight uses mid-budget world/experience recall, not reflect or procedural learning.

The final cap uses cl100k_base including metadata. A whole record is skipped when it does not fit;
this can disadvantage large graph episodes relative to short RAG chunks. Skipped counts are retained.
No gold-based query expansion or document selection is performed.

Expected JSON fields must match type and value. Source-ID checks verify context membership and
at least one expected evidence ID, not semantic entailment. Canary checks inspect all retrieval
results before packing plus the answer. Empty memory cannot be a successful positive control.
These are namespace tests, not authentication or complete access-control certification.

The body-free gateway ledger records model IDs, token usage and latency. Cached input is not the
same as monetary cost; missing usage is unknown. Match CLI and gateway model settings and inspect
returned model IDs. Top-level dependencies are pinned, not all transitives or model-weight revisions.
Run outputs contain source data and must remain private unless separately reviewed.

The included inactive CI example checks fixtures, grading and publication hygiene, not native API service operation. GitHub Actions is not enabled in this initial publication.
Live integration evidence, when available, is reported separately. A successful process can have
failed answers: inspect answer_pass rather than only the exit code.
