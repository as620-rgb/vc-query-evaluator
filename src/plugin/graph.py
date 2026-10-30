"""The knowledge graph of the bundled 40 YC companies (data/companies.json) and the query tools."""

from __future__ import annotations

import json
import re
from functools import cache
from pathlib import Path

from contract import (
    Edge,
    Neighborhood,
    NeighborsInput,
    NeighborsOutput,
    NodeKind,
    NodeRef,
    Peer,
    PeerInput,
    PeerOutput,
    PinOutput,
    Relation,
)

DATA = Path(__file__).parent / "data" / "companies.json"
MOST_NODES = 20
SEPARATORS = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    return SEPARATORS.sub("-", text.lower()).strip("-")


@cache
def graph() -> tuple[dict[str, NodeRef], tuple[Edge, ...]]:
    """Every node by id, and every edge (company -> batch, location or industry tag)."""
    nodes: dict[str, NodeRef] = {}
    edges: list[Edge] = []
    for company in json.loads(DATA.read_text(encoding="utf-8")):
        own = f"company:{company['slug']}"
        nodes[own] = NodeRef(id=own, kind=NodeKind.COMPANY, name=company["name"])
        targets = [
            (Relation.IN_BATCH, NodeKind.BATCH, "batch", company["batch"]),
            (Relation.LOCATED_IN, NodeKind.LOCATION, "location", company["location"]),
        ] + [(Relation.IN_INDUSTRY, NodeKind.INDUSTRY, "industry", tag) for tag in company["industries"]]
        for relation, kind, prefix, name in targets:
            target = f"{prefix}:{slugify(name)}"
            nodes[target] = NodeRef(id=target, kind=kind, name=name)
            edges.append(Edge(source=own, relation=relation, target=target))
    return nodes, tuple(edges)


def touching(node: str, relation: Relation) -> list[Edge]:
    return [edge for edge in graph()[1] if edge.relation is relation and node in (edge.source, edge.target)]


def neighbors(request: NeighborsInput, workspace: Path) -> NeighborsOutput:
    if not 1 <= len(request.nodes) <= MOST_NODES or len(set(request.nodes)) != len(request.nodes):
        raise ValueError(f"give 1 to {MOST_NODES} distinct node ids")
    nodes = graph()[0]
    unknown = [node for node in request.nodes if node not in nodes]
    if unknown:
        raise ValueError(f"no node {unknown}: ids look like company:doordash or batch:summer-2013")
    results = []
    for node in request.nodes:
        found = {edge.target if edge.source == node else edge.source for edge in touching(node, request.relation)}
        results.append(Neighborhood(node=node, neighbors=[nodes[other] for other in sorted(found)]))
    return NeighborsOutput(relation=request.relation, results=results)


def pin_peers(task: PeerInput, workspace: Path) -> PinOutput:
    """The answer key, with every edge it rests on."""
    nodes = graph()[0]
    start = f"company:{task.company}"
    if start not in nodes:
        raise ValueError(f"no company with slug {task.company!r}")
    if task.industry != task.industry.strip():
        raise ValueError("industry must not start or end with spaces")
    hubs = touching(start, task.via)
    shared: dict[str, list[str]] = {}
    evidence = list(hubs)
    for hub in hubs:
        for edge in touching(hub.target, task.via):
            if edge.source != start:
                shared.setdefault(edge.source, []).append(hub.target)
                evidence.append(edge)
    wanted = f"industry:{slugify(task.industry)}"
    peers = []
    for candidate in sorted(shared):
        if task.industry:
            tags = touching(candidate, Relation.IN_INDUSTRY)
            evidence.extend(edge for edge in tags if edge not in evidence)
            if not any(edge.target == wanted for edge in tags):
                continue
        peers.append(Peer(id=candidate, name=nodes[candidate].name, via=sorted(shared[candidate])))
    return PinOutput(answer=PeerOutput(start=start, peers=peers, count=len(peers)), evidence=evidence)
