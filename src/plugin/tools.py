"""
Graph RAG Multi-hop Retrieval Tools (Task 3)
"""

from contract import (
    GraphRAGInput,
    GraphRAGOutput,
    PathStep,
)


def multi_hop_query_tool(input_data: GraphRAGInput) -> GraphRAGOutput:
    nodes = input_data.nodes or []
    edges = input_data.edges or []
    start_id = input_data.start_node_id
    
    # Build an adjacency list
    adj: dict[str, list[tuple[str, str]]] = {}
    for edge in edges:
        adj.setdefault(edge.source_id, []).append((edge.target_id, edge.relation))
        adj.setdefault(edge.target_id, []).append((edge.source_id, f"REV_{edge.relation}"))

    # 1 Hop: Find nodes associated with the starting node via Batch / Industry relationships
    hop1_neighbors = adj.get(start_id, [])
    
    target_companies: set[str] = set()
    paths: list[list[PathStep]] = []

    # 2 Hops: Find other companies that share the same Batch / Industry
    for middle_id, rel1 in hop1_neighbors:
        hop2_neighbors = adj.get(middle_id, [])
        for target_id, rel2 in hop2_neighbors:
            if target_id != start_id and target_id.startswith("company:"):
                company_name = target_id.replace("company:", "").replace("_", " ").title()
                target_companies.add(company_name)
                
                step1 = PathStep(hop=1, from_node=start_id, relation=rel1, to_node=middle_id)
                step2 = PathStep(hop=2, from_node=middle_id, relation=rel2, to_node=target_id)
                paths.append([step1, step2])

    target_list = sorted(list(target_companies))
    summary = f"Found {len(target_list)} related companies through multi-hop graph retrieval."

    return GraphRAGOutput(
        start_node=start_id,
        target_companies=target_list,
        traversal_paths=paths,
        reasoning_summary=summary,
        total_hops_executed=2
    )
