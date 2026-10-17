# Private calibration: 17 October 2026

Author-reported aggregates; messages and per-source traces are private. Public fictional examples
and the separately authored public runner do not reproduce these exact numbers.

## Conditions

14 records, 8002 characters:13 selected source records/artifacts and1 synthetic control.
12 questions:10 work questions and2 initial scope controls. Several questions share a correction.
One GLM-5.3-Flash pass on known cases, not a held-out statistical ranking or strict historical replay.
Shared local multilingual MiniLM embeddings,384 dimensions; final context1536 cl100k_base tokens.
Search latency excludes answer generation. Source IDs are syntactic provenance checks, not entailment.
No production integration or real external sends were performed.

| Variant | Work /10 | All /12 | Mean search ms | Native prompt tokens | Native completion tokens |
|---|---:|---:|---:|---:|---:|
| RAG |10|12|64.74|0|0|
| Hindsight1.0.0 |9|11|150.75|50546|5554|
| Mem0 OSS2.2.1 |9|10|57.02|127206|3263|
| Graphiti0.31.1 edges |1|2|102.99|139358|7377|
| Graphiti combined, same index |1|3|120.69|reused|reused|

See private-calibration-scores.csv. Zero combined ingestion in the CSV means reuse, not free graphs.
Memory token counts exclude answers but include cached input; they are not monetary cost.
Hindsight also includes successful startup model validation. Two early connection failures have
no fabricated token usage. RAG has local embedding compute and answer calls despite no extraction LLM.

## Failure observations

An uncertain weekday was made certain in extracted memory. Mem0 and Hindsight failed this question.
A later diagnostic fetched permitted originals using IDs already returned by retrieval; both then
preserved uncertainty under the same cap. The main scores were not replaced.

Graphiti stored a policy episode with zero extracted nodes and edges. Combined retrieval did not
improve the work-question count. Mem0 did not retain the first synthetic private code; absence from
another scope was therefore not accepted as proof of isolation. Subsequent two-namespace probes
used meaningful fictional relational facts and positive/negative controls.

An initially ambiguous synthetic question was corrected before non-RAG question runs. The original
RAG failure remained in private diagnostic history. These calibration edits must not be called blind
held-out evaluation. All four backends subsequently passed namespace readback controls after actual
owned-service/client restarts. Graphiti used combined search for those controls.

## Configuration and limits

RAG: BM25+dense RRF,240-token chunks,200 stride. Hindsight:PostgreSQL/pgvector,native text,RRF,
world/experience recall; no reflect/observation-based consolidation test. Mem0:local Qdrant,inferred
facts; optional spaCy NLP was absent and fallback warnings were observed. Graphiti:FalkorDB4.16.0,
OpenAI-compatible JSON-object client,edge search,then combined RRF using the same graph.

This tiny statement/policy corpus has no substantial multi-hop evaluation. Model, extraction,
ontology, language, database, retrieval and packing all contribute. Whole over-budget graph episodes
were skipped while RAG had smaller chunks: equal final caps do not mean equally good allocation.
The result is not a verdict on graphs or on Graphiti's capabilities in other configurations.

No claims about full-archive quality, autonomous procedure learning, full authorization, revocation,
poisoning resistance, production throughput, multimodal memory or multi-day execution are made.
