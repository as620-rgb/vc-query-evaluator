"""
Graph RAG Evaluator Verifier (Task 3)
"""

from typing import Any


def verify_task(task_input: Any, agent_output: Any, workspace_path: str) -> dict:
    constraints = []

    # 1. Output Field Completeness Verification
    has_rag = hasattr(agent_output, "target_companies") and hasattr(agent_output, "traversal_paths")
    if not has_rag:
        return {
            "score": 0.0,
            "constraints": [{
                "id": "shape-check",
                "ok": False,
                "message": "agent_output missing 'target_companies' or 'traversal_paths'"
            }]
        }

    targets = agent_output.target_companies
    paths = agent_output.traversal_paths

    # ---- Constraint 1: Multi-hop matching results are non-empty ----
    ok_targets = len(targets) > 0
    constraints.append({
        "id": "non-empty-targets",
        "ok": ok_targets,
        "message": "" if ok_targets else "No target companies returned for multi-hop query"
    })

    # ---- Constraint 2: Integrity of multi-hop reasoning paths (must include a 2-hop path) ----
    ok_paths = len(paths) > 0 and all(len(path) == 2 for path in paths)
    constraints.append({
        "id": "valid-two-hop-paths",
        "ok": ok_paths,
        "message": "" if ok_paths else "Traversal paths must be valid 2-hop sequences"
    })

    # ---- Constraint 3: Jump Depth Determination ----
    ok_hops = getattr(agent_output, "total_hops_executed", 0) == 2
    constraints.append({
        "id": "hop-count-exact",
        "ok": ok_hops,
        "message": "" if ok_hops else "total_hops_executed must equal 2"
    })

    score = 1.0 if all(c["ok"] for c in constraints) else 0.0
    return {
        "score": score,
        "constraints": constraints
    }
