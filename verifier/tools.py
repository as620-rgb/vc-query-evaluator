"""neighbors and pin_peers calls."""

from .checks import result
from .rules import MOST_NODES, peers


def edges_of(pinned):
    return [(edge.source, edge.relation.value, edge.target) for edge in pinned.evidence]


def plain_answer(answer):
    return {peer.id: list(peer.via) for peer in answer.peers}


class Neighbors:
    @staticmethod
    def verify_input(value):
        if not 1 <= len(value.nodes) <= MOST_NODES or len(set(value.nodes)) != len(value.nodes):
            return result(False, f"give 1 to {MOST_NODES} distinct node ids")
        return result(True, "input is valid")

    @staticmethod
    def verify_output(input_value, output_value, workspace):
        if [entry.node for entry in output_value.results] != list(input_value.nodes):
            return result(False, "the results are not the nodes asked for, in order")
        if output_value.relation != input_value.relation:
            return result(False, "the results are for another relation")
        for entry in output_value.results:
            ids = [neighbor.id for neighbor in entry.neighbors]
            if ids != sorted(set(ids)) or entry.node in ids:
                return result(False, f"{entry.node}: neighbors must be distinct, sorted and not the node itself")
        return result(True, "neighbors listed")


class Pin:
    @staticmethod
    def verify_input(value):
        if value.industry != value.industry.strip():
            return result(False, "industry must not start or end with spaces")
        return result(True, "input is valid")

    @staticmethod
    def verify_output(input_value, output_value, workspace):
        answer = output_value.answer
        if answer.start != f"company:{input_value.company}" or answer.count != len(answer.peers):
            return result(False, "the answer key's start or count is wrong")
        recomputed = peers(answer.start, input_value.via.value, input_value.industry, edges_of(output_value))
        if plain_answer(answer) != recomputed:
            return result(False, "the answer key does not follow from its own evidence")
        return result(True, f"answer key has {answer.count} peers")
