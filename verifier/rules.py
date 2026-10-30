"""Peers recomputed from a list of edges: pure standard library, so the sandboxed verifier uses it."""

import re

MOST_NODES = 20
SEPARATORS = re.compile(r"[^a-z0-9]+")


def slugify(text):
    return SEPARATORS.sub("-", text.lower()).strip("-")


def peers(start, via, industry, edges):
    """{peer id: sorted shared node ids} that the edges (source, relation, target) give for the query."""
    hubs = {target for source, relation, target in edges if source == start and relation == via}
    shared = {}
    for source, relation, target in edges:
        if relation == via and target in hubs and source != start:
            shared.setdefault(source, set()).add(target)
    if industry:
        wanted = f"industry:{slugify(industry)}"
        tagged = {source for source, relation, target in edges if relation == "IN_INDUSTRY" and target == wanted}
        shared = {peer: nodes for peer, nodes in shared.items() if peer in tagged}
    return {peer: sorted(nodes) for peer, nodes in shared.items()}
