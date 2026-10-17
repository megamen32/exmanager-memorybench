# A graph alongside RAG, not instead of evidence

Architecture proposal, not an implemented ExManager integration.

RAG is a retrieval-augmented answering pattern. A graph is a representation and index that can
participate in it. Graphiti builds temporal graphs of entities, relations and source episodes,
and offers hybrid retrieval. These are not mutually exclusive alternatives.

Useful manager relationships:

```
person --owns--> task --blocks--> milestone --belongs_to--> project
person --member_of--> team
agreement --supported_by--> message
agreement --supersedes--> previous_agreement
```

Use authoritative task IDs, memberships and canonical identities where available. Do not ask
an LLM to guess whether two accounts belong to the same person from a matching display name.
Let extraction propose additional relations; retain the source, who asserted them, uncertainty,
observed time, valid time, scope and supersession status.

Proposed path: scoped source search + scoped graph expansion -> fetch permitted originals ->
bounded context -> answer/proposed action -> separate authorization and durable action state.
A revoked source must also be removed from derived summaries and accessible cache results.
Filter permissions before graph traversal and source fetch, not only after answer generation.

A small node/edge table can be a sufficient initial prototype. A separate graph service should
justify its operational cost. An inferred graph is not durable execution state for a pending send.

## Next experiment

Hold out entire episodes containing two-to-four-hop dependencies, changed owners, aliases across
channels, expired agreements and private edges. Include negative questions and useful authorized
positive controls. Compare source RAG, native graph retrieval and RAG + graph + source readback at
matched context/model budgets with at least three repeats.

Report extraction omissions, raw-source recall, context-packing loss, action accuracy, forbidden
context, latency and ingestion/maintenance costs separately. Decide whether to keep the graph
from its incremental benefit, not a chart of ten already-known status questions.

Upstream architecture: https://github.com/getzep/graphiti
