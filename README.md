# ExManager MemoryBench

**Please do not turn probably into a calendar invite.**

A standalone public harness for hybrid RAG, Hindsight, Graphiti and Mem0 OSS.
It contains fictional examples and aggregate private calibration scores, not private messages.

## Private calibration, not a leaderboard

| Configuration | Work questions passed | Mean retrieval, ms |
|---|---:|---:|
| RAG: BM25 + dense + reciprocal-rank fusion | 10/10 | 64.74 |
| Hindsight 1.0.0 | 9/10 | 150.75 |
| Mem0 OSS 2.2.1 | 9/10 | 57.02 |
| Graphiti 0.31.1, edges | 1/10 | 102.99 |
| Graphiti 0.31.1, combined, same index | 1/10 | 120.69 |

Author-reported private calibration: fourteen source records, ten related work questions,
one GLM-5.3-Flash run and a 1536-token retrieved-context cap. Search latency excludes answers.
The source corpus is private. Fictional public examples do not reproduce these scores.
Several questions share an episode. This is not evidence that RAG generally beats graphs.

The useful failure: an uncertain weekday became a confirmed appointment after fact extraction.
For Hindsight and Mem0, reading permitted originals already linked by retrieval fixed that
specific answer under the same context cap. Original scores were not replaced.

This public implementation is separately authored, not an export of a production workspace.
No private messages, contact details, keys, database snapshots or internal endpoints are included.

Full instructions, source and offline checks are included in the initial release.

[Русский](README.ru.md) · [Protocol](docs/PROTOCOL.md) · [Graph proposal](docs/GRAPH.md) · [Calibration report](reports/2026-10-17-private-calibration.md) · [CSV](reports/private-calibration-scores.csv)

## What is included

Native adapters for all four backends, plus Graphiti combined retrieval; a local model/embedding
gateway; chronological fixture validation; typed JSON grading; source-ID checks; pre-packing
namespace canaries; resumable ingestion receipts; and 15 dependency-free contract tests.

Public fixtures are newly authored:9 fictional events/12 questions and a smaller2-event/3-question
smoke set. No private source text or private trace is needed for these examples. They are calibration
examples, not a hidden test set. The public runner is a separate implementation, not an exact export
of the original private test code.

## Offline checks

Python3.10+ is sufficient for these checks; native backends below use Python3.12.

```bash
python -m unittest discover -s tests -v
python run.py rag --output .runs/validation --validate-only
```

These checks need no API credentials, installed memory engine or running database. The inactive [CI example](docs/ci-example.yml) contains these
checks, not live LLM evaluation. GitHub Actions is not enabled in this initial publication:the
available publishing credential does not have workflow permission. They do not certify native service compatibility or answer quality.

## Run the public examples

On Linux or macOS, use a dedicated environment. No production application is modified.
The pinned requirements are the top-level versions observed in the private experiment, not a
complete transitive lock or a guarantee that every platform will install them unchanged.

```bash
python3.12 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env locally: an authorized OpenAI-compatible endpoint, its key and one explicit model.
# Then export the configuration in each terminal used below:
set -a
. ./.env
set +a

# Terminal 1, foreground; do not expose this unauthenticated local gateway to a public interface.
uvicorn src.gateway:app --host 127.0.0.1 --port 18981 --no-access-log
```

The gateway downloads multilingual MiniLM embeddings and runs them locally on CPU. It uses the
configured upstream only for LLM calls. Its ledger records model IDs, counts and latency, not prompt
bodies or credentials. Inputs sent to your provider remain subject to that provider's data policy.
Set `MEMBENCH_DISABLE_THINKING=true` only for a provider supporting that option. Choose one actual
model, not an automatic fallback chain, and inspect the recorded response model IDs.

```bash
# Terminal 2, same virtual environment and exported .env:
python run.py rag --output .runs/example
python run.py mem0 --output .runs/example

# Smaller optional dataset, in a separate output directory:
python run.py rag --events examples/smoke/events.jsonl \
  --cases examples/smoke/cases.jsonl --output .runs/smoke
```

RAG persists its chunks/vectors under the run directory. Mem0 uses embedded local Qdrant storage,
not the Mem0 hosted service. Neither command requires a separate database server.

### Hindsight and Graphiti

These adapters require separately provisioned, isolated native services. This public repository
is a harness, not a turnkey production deployment or an installer for all external services.

- **Hindsight:** run its API with a dedicated PostgreSQL/pgvector database. Set
  `MEMBENCH_HINDSIGHT_URL` (default `http://127.0.0.1:18988`). Configure its LLM and embedding
  providers to use the same gateway's `/hindsight/v1` endpoint and384-dimensional embeddings.
  Follow [Hindsight configuration](https://hindsight.vectorize.io/developer/configuration).
- **Graphiti:** provision a dedicated FalkorDB instance. Set `MEMBENCH_FALKOR_HOST`,
  `MEMBENCH_FALKOR_PORT` (defaults `127.0.0.1`, `16379`) and `MEMBENCH_FALKOR_PASSWORD` as appropriate.
  See [Graphiti](https://github.com/getzep/graphiti) and [FalkorDB](https://github.com/FalkorDB/FalkorDB).

A container's loopback address is not the host's loopback address. Supply an actually reachable,
private gateway route; do not solve this by exposing keys or opening an unauthenticated public port.
The gateway model must equal `MEMBENCH_MODEL`; use the same embedding model/dimension for every arm.

```bash
python run.py hindsight --output .runs/example
python run.py graphiti --output .runs/example
# Same stored graph, a separately scored retrieval configuration:
python run.py graphiti-combined --output .runs/example

# New process, no source re-ingestion; preserves the original case results:
python run.py mem0 --output .runs/example --read-only
```

An output directory receives a random namespace and an input/configuration/source fingerprint.
Changed inputs or code require a new output directory. Do not resubmit an unacknowledged native
write; reconcile it or start a new isolated experiment. Graph initialization may still create
indexes in read-only mode:that mode means no source re-ingestion, not a database read-only transaction.

Results are in `.runs/<name>/results/<arm>/`, including complete retrieved records, packed context,
answers, token usage and grades. `answer_pass` matters:process completion does not mean every answer
passed. Citation checks establish ID membership, not semantic entailment. Private datasets make
these output files private too. Keep `.runs/`, `.env`, database files and logs out of Git.

## Resource and evaluation limits

One arm at a time. The runner has a3600-second subprocess deadline; the gateway serializes LLM
calls and stops subsequent calls after600 attempts or1.5M reported tokens by default. A request
already in flight can exceed the token threshold. Missing usage is unknown, not free. This is a
run guard, not a billing cap. The gateway ledger is cumulative until a new isolated ledger directory
is selected. Configure OS/container memory, CPU, disk and process limits appropriate to your host;
this public launcher does not enforce the original private container budgets.

Whole records exceeding the context budget are skipped and counted. This may disadvantage long
graph episodes relative to chunked RAG. The private test had no substantial multi-hop questions,
no repeated trials and no production load. See the [protocol](docs/PROTOCOL.md) before interpreting scores.

## Graphs are not the opposite of RAG

A graph can enrich retrieval with responsibility, dependencies and temporal relationships.
For a manager, the proposed next comparison is source RAG versus source RAG plus a graph, followed
by reading authorized originals. A graph edge must not become a stronger claim than its source.
[The graph proposal](docs/GRAPH.md) describes the next held-out multi-hop experiment; it is not an
implemented production integration.

MIT for this harness and its fictional examples. Dependencies retain their own licenses.
