# VC Peer Query

A `nanoagent.plugin/v0001` plugin, built on the structure of NanoAgent's reference plugin,
[arxiv-source](https://github.com/zeyuyang8/arxiv-source). It answers multi-hop questions over a knowledge
graph of 40 YC companies (built from the bundled directory snapshot, `src/plugin/data/companies.json`):
"which companies share a batch with DoorDash?", "which San Francisco companies near Brex are B2B?". The agent
walks the graph hop by hop with one tool; everything runs offline, so every run sees the same graph.

## Tools

| Tool | Does | Code |
|---|---|---|
| `neighbors` | Lists the neighbors of up to 20 nodes by one relation, in either direction | `src/plugin/graph.py` |
| `pin_peers` | Reference tool: the peers the graph gives, with every edge they rest on (hidden from the agent) | `src/plugin/graph.py` |

### Tasks

| Task | Does | Runner |
|---|---|---|
| `find-peers` | Finds every company sharing a batch, location or industry with a company, optionally filtered by an industry tag | `agent`, with `neighbors`; reference `pin_peers` |

Example input: `{"company": "amplitude", "via": "IN_INDUSTRY", "industry": "Analytics"}`; the answer is Heap
(via `industry:analytics` and `industry:b2b`) and Segment (the same two).

### Verifier

`verify_task` recomputes the peers from the pinned evidence edges (`verifier/rules.py`), refuses an answer
key that does not follow from its own evidence, and checks the submission in nine checks: `start`, `count`,
`sorted`, `no-duplicates`, `no-missing`, `no-extra`, `names-exact`, `via-exact` and `paths-exist` (every
claimed path start → node ← peer is a real pair of edges).

## Layout

```text
.
├── nanoagent.yaml   # manifest: id, runtime, permissions, tools, tasks
├── contract.py      # each tool's and task's typed input and output
├── src/plugin/      # the MCP server (__main__.py) and graph.py; data/ holds the company snapshot
├── tests/           # verifier tests: correct, missing, extra, wrong, malformed and boundary cases
├── ui/              # renderers (outputs drawn from their JSON Schema)
├── product/         # product page: product.yaml and icon.svg
└── verifier/        # deterministic verifier: rules.py, tools.py, task.py, checks.py
```

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

Publishing checks every plugin rule: push the plugin to a public GitHub repository and submit its URL
on RUSH Lab's Marketplace.
