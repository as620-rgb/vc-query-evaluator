"""
Graph RAG Multi-hop Query Evaluator (Task 3)
Typed input and output declarations using nanoagent.plugin.contract standards.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Optional
from slimconfig import Output


class Tool(Enum):
    GRAPH_TRAVERSE = "graph_traverse"
    MULTI_HOP_REASON = "multi_hop_reason"


class Task(Enum):
    GRAPH_RAG_QUERY = "graph-rag-query"


@dataclass
class Node(Output):
    id: str
    label: str
    name: str


@dataclass
class Edge(Output):
    source_id: str
    target_id: str
    relation: str


@dataclass
class GraphRAGInput(Output):
    query: Annotated[str, "Natural language multi-hop query, e.g., 'Find batch-mates of DoorDash in Consumer industry'"]
    start_node_id: Annotated[str, "Starting entity node ID, e.g., 'company:doordash'"]
    max_hops: Annotated[int, "Maximum graph hop depth"] = 2
    nodes: list[Node] = None
    edges: list[Edge] = None


@dataclass
class PathStep(Output):
    hop: int
    from_node: str
    relation: str
    to_node: str


@dataclass
class GraphRAGOutput(Output):
    start_node: str
    target_companies: list[str]
    traversal_paths: list[list[PathStep]]
    reasoning_summary: str
    total_hops_executed: int


TOOLS = {
    Tool.GRAPH_TRAVERSE: (GraphRAGInput, GraphRAGOutput),
}

TASKS = {
    Task.GRAPH_RAG_QUERY: (GraphRAGInput, GraphRAGOutput),
}