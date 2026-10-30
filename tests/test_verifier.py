from __future__ import annotations

from pathlib import Path

import pytest
from slimconfig import build_output, plain_output

import verifier
from contract import NeighborsInput, NeighborsOutput, PeerInput, PeerOutput, PinOutput
from plugin.graph import neighbors, pin_peers


def query(company: str, via: str, industry: str = "") -> PeerInput:
    return build_output({"company": company, "via": via, "industry": industry}, PeerInput)


def key(given: PeerInput, workspace: Path) -> PinOutput:
    return build_output(plain_output(pin_peers(given, workspace)), PinOutput)


def gold(given: PeerInput, workspace: Path) -> dict:
    return plain_output(key(given, workspace).answer)


def check(given: PeerInput, submission: dict, workspace: Path) -> dict:
    output = build_output(submission, PeerOutput)
    return verifier.verify_task("find-peers", given, output, key(given, workspace), str(workspace))


def failing(verdict: dict) -> list[str]:
    return [entry["id"] for entry in verdict["details"]["constraints"] if not entry["ok"]]


def ids(answer: dict) -> list[str]:
    return [peer["id"] for peer in answer["peers"]]


def test_batch_peers(tmp_path: Path) -> None:
    answer = gold(query("doordash", "IN_BATCH"), tmp_path)
    assert answer["start"] == "company:doordash" and ids(answer) == ["company:casetext"]  # both Summer 2013


def test_industry_peers_share_one_or_two_tags(tmp_path: Path) -> None:
    answer = gold(query("amplitude", "IN_INDUSTRY"), tmp_path)
    via = {peer["id"]: peer["via"] for peer in answer["peers"]}
    assert via["company:segment"] == ["industry:analytics", "industry:b2b"]
    assert via["company:gitlab"] == ["industry:b2b"]
    assert answer["count"] == 14  # every other B2B company


def test_the_industry_filter_reads_the_peers_tags(tmp_path: Path) -> None:
    answer = gold(query("brex", "LOCATED_IN", "B2B"), tmp_path)
    assert "company:gitlab" in ids(answer) and "company:doordash" not in ids(answer)
    assert ids(gold(query("brex", "LOCATED_IN", "b2b"), tmp_path)) == ids(answer)  # case does not matter
    assert ids(gold(query("amplitude", "IN_INDUSTRY", "Analytics"), tmp_path)) == ["company:heap", "company:segment"]


def test_approves_the_correct_answer(tmp_path: Path) -> None:
    given = query("amplitude", "IN_INDUSTRY", "Analytics")
    verdict = check(given, gold(given, tmp_path), tmp_path)
    assert verdict["valid"] is True and verdict["score"] == 1.0


def test_boundary_no_peers(tmp_path: Path) -> None:
    given = query("equipmentshare", "LOCATED_IN")  # the only company in Columbia, MO
    assert gold(given, tmp_path) == {"start": "company:equipmentshare", "peers": [], "count": 0}
    assert check(given, {"start": "company:equipmentshare", "peers": [], "count": 0}, tmp_path)["valid"] is True
    assert ids(gold(query("doordash", "IN_INDUSTRY", "Space Mining"), tmp_path)) == []


def test_rejects_a_missing_peer(tmp_path: Path) -> None:
    given = query("amplitude", "IN_INDUSTRY", "Analytics")
    answer = gold(given, tmp_path)
    answer["peers"], answer["count"] = answer["peers"][:1], 1
    assert failing(check(given, answer, tmp_path)) == ["no-missing"]


def test_rejects_a_peer_that_fails_the_filter(tmp_path: Path) -> None:
    given = query("amplitude", "IN_INDUSTRY", "Analytics")
    answer = gold(given, tmp_path)
    answer["peers"].insert(0, {"id": "company:gitlab", "name": "GitLab", "via": ["industry:b2b"]})
    answer["count"] = 3
    assert failing(check(given, answer, tmp_path)) == ["no-extra"]


def test_rejects_a_fabricated_path(tmp_path: Path) -> None:
    given = query("doordash", "IN_BATCH")
    answer = gold(given, tmp_path)
    answer["peers"].append({"id": "company:segment", "name": "Segment", "via": ["batch:summer-2013"]})
    answer["count"] = 2
    assert set(failing(check(given, answer, tmp_path))) == {"no-extra", "paths-exist"}


def test_rejects_incomplete_via_wrong_names_order_and_count(tmp_path: Path) -> None:
    given = query("amplitude", "IN_INDUSTRY", "Analytics")
    answer = gold(given, tmp_path)
    one = {**answer, "peers": [{**answer["peers"][1], "via": ["industry:b2b"]}, answer["peers"][0]]}
    assert set(failing(check(given, one, tmp_path))) == {"via-exact", "sorted"}
    renamed = {**answer, "peers": [{**answer["peers"][0], "name": "heap"}, answer["peers"][1]]}
    assert failing(check(given, renamed, tmp_path)) == ["names-exact"]
    assert failing(check(given, {**answer, "count": 3}, tmp_path)) == ["count"]
    assert failing(check(given, {**answer, "start": "doordash"}, tmp_path)) == ["start"]
    doubled = {**answer, "peers": answer["peers"] + answer["peers"][1:], "count": 3}
    assert failing(check(given, doubled, tmp_path)) == ["no-duplicates"]


def test_rejects_a_tampered_answer_key(tmp_path: Path) -> None:
    given = query("doordash", "IN_BATCH")
    pinned = plain_output(key(given, tmp_path))
    pinned["answer"]["peers"] = []
    pinned["answer"]["count"] = 0
    tampered = build_output(pinned, PinOutput)
    assert verifier.verify_output("pin_peers", given, tampered, str(tmp_path))["valid"] is False
    output = build_output(pinned["answer"], PeerOutput)
    assert verifier.verify_task("find-peers", given, output, tampered, str(tmp_path))["valid"] is False
    assert verifier.verify_task("find-peers", given, output, None, str(tmp_path))["valid"] is False


def test_neighbors_tool_and_its_checks(tmp_path: Path) -> None:
    given = build_output({"nodes": ["company:heap", "industry:analytics"], "relation": "IN_INDUSTRY"}, NeighborsInput)
    out = build_output(plain_output(neighbors(given, tmp_path)), NeighborsOutput)
    assert [n.id for n in out.results[0].neighbors] == ["industry:analytics", "industry:b2b"]
    assert [n.id for n in out.results[1].neighbors] == ["company:amplitude", "company:heap", "company:segment"]
    assert verifier.verify_output("neighbors", given, out, str(tmp_path))["valid"] is True
    with pytest.raises(ValueError, match="no node"):
        neighbors(build_output({"nodes": ["company:openai"], "relation": "IN_BATCH"}, NeighborsInput), tmp_path)
    for nodes in ([], ["company:heap", "company:heap"], [f"company:{i}" for i in range(21)]):
        bad = build_output({"nodes": nodes, "relation": "IN_BATCH"}, NeighborsInput)
        assert verifier.verify_input("neighbors", bad)["valid"] is False


def test_refuses_bad_queries(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no company"):
        pin_peers(query("openai", "IN_BATCH"), tmp_path)
    assert verifier.verify_input("pin_peers", query("heap", "IN_BATCH", " B2B"))["valid"] is False
