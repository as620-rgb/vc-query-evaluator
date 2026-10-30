"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    NEIGHBORS = "neighbors"
    PIN_PEERS = "pin_peers"


class Task(Enum):
    FIND_PEERS = "find-peers"


class NodeKind(Enum):
    COMPANY = "Company"
    BATCH = "Batch"
    INDUSTRY = "Industry"
    LOCATION = "Location"


class Relation(Enum):
    IN_BATCH = "IN_BATCH"
    IN_INDUSTRY = "IN_INDUSTRY"
    LOCATED_IN = "LOCATED_IN"


NODE_ID = "A node id, e.g. company:doordash, batch:summer-2013, industry:analytics, location:boston-ma-usa"


@dataclass
class PeerInput(Output):
    company: Annotated[str, "The starting company's slug, e.g. doordash"]
    via: Annotated[Relation, "The relation both companies share a node by: IN_BATCH, IN_INDUSTRY or LOCATED_IN"]
    industry: Annotated[
        str,
        "An industry tag, e.g. Analytics: keep only peers with an IN_INDUSTRY edge to its node, industry:<the tag in "
        "lowercase, each run of other characters one hyphen> (top or sub-industry); empty for any",
    ]


@dataclass
class Peer(Output):
    id: Annotated[str, "The peer's company node id"]
    name: Annotated[str, "The peer's name"]
    via: Annotated[list[str], "Every node id the peer shares with the starting company by the relation, sorted"]


@dataclass
class PeerOutput(Output):
    start: Annotated[str, "The starting company's node id"]
    peers: Annotated[list[Peer], "Every peer, sorted by id; [] for none"]
    count: Annotated[int, "How many peers"]


@dataclass
class NodeRef(Output):
    id: Annotated[str, NODE_ID]
    kind: NodeKind
    name: str


@dataclass
class Edge(Output):
    source: Annotated[str, "A company node id"]
    relation: Relation
    target: Annotated[str, NODE_ID]


@dataclass
class NeighborsInput(Output):
    nodes: Annotated[list[Annotated[str, NODE_ID]], "1 to 20 distinct node ids"]
    relation: Relation


@dataclass
class Neighborhood(Output):
    node: Annotated[str, NODE_ID]
    neighbors: Annotated[list[NodeRef], "Every node joined to it by the relation, in either direction, sorted by id"]


@dataclass
class NeighborsOutput(Output):
    relation: Relation
    results: Annotated[list[Neighborhood], "One entry per node asked, in order"]


@dataclass
class PinOutput(Output):
    answer: PeerOutput
    evidence: Annotated[list[Edge], "Every edge the answer rests on and every edge that rules a candidate out"]


TOOLS = {
    Tool.NEIGHBORS: (NeighborsInput, NeighborsOutput),
    Tool.PIN_PEERS: (PeerInput, PinOutput),
}
TASKS = {Task.FIND_PEERS: (PeerInput, PeerOutput)}
