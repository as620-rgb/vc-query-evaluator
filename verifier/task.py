"""find-peers: the submitted peers against the peers recomputed from the pinned graph evidence."""

from .checks import constraint, result, verdict
from .rules import peers
from .tools import edges_of


def verify_task(arguments, output, reference, workspace):
    if reference is None:
        return result(False, "no answer key was pinned")
    start = f"company:{arguments.company}"
    edges = edges_of(reference)
    expected = peers(start, arguments.via.value, arguments.industry, edges)
    if expected != {peer.id: list(peer.via) for peer in reference.answer.peers}:
        return result(False, "the pinned answer key does not follow from its evidence")
    names = {peer.id: peer.name for peer in reference.answer.peers}
    edge_set = set(edges)
    via = arguments.via.value

    ids = [peer.id for peer in output.peers]
    duplicates = sorted({peer for peer in ids if ids.count(peer) > 1})
    missing = sorted(peer for peer in expected if peer not in ids)
    extra = sorted(peer for peer in set(ids) if peer not in expected)
    wrong_names = [f"{p.id}: expected {names[p.id]!r}, got {p.name!r}" for p in output.peers if p.id in names and p.name != names[p.id]]
    wrong_via = [f"{p.id}: expected {expected[p.id]}, got {list(p.via)}" for p in output.peers if p.id in expected and list(p.via) != expected[p.id]]
    unsupported = [
        f"{p.id} via {node}"
        for p in output.peers
        for node in p.via
        if (start, via, node) not in edge_set or (p.id, via, node) not in edge_set
    ]

    return verdict([
        constraint("start", "start is the company's node id", output.start == start, start, output.start),
        constraint("count", "count is the number of peers submitted", output.count == len(ids), len(ids), output.count),
        constraint("sorted", "peers are sorted by id", ids == sorted(ids), sorted(ids), ids, "peers are not sorted by id"),
        constraint("no-duplicates", "each peer appears once", not duplicates, [], duplicates, f"repeated: {duplicates}"),
        constraint("no-missing", "every peer is found", not missing, [], missing, f"{len(missing)} peers missing: {missing}"),
        constraint("no-extra", "no company that is not a peer", not extra, [], extra, f"{len(extra)} are not peers: {extra}"),
        constraint("names-exact", "every peer's name is its company's", not wrong_names, [], wrong_names,
                   wrong_names[0] if wrong_names else ""),
        constraint("via-exact", "every peer lists exactly the nodes it shares, sorted", not wrong_via, [], wrong_via,
                   wrong_via[0] if wrong_via else ""),
        constraint("paths-exist", "every claimed path start -> node <- peer is in the graph", not unsupported, [],
                   unsupported, f"no such path: {unsupported[0] if unsupported else ''}"),
    ])
