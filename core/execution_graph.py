from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ExecutionNode:
    name: str
    status: str = "pending"
    attempts: int = 0
    metadata: Dict[str, object] = field(default_factory=dict)


class ExecutionGraph:
    """Minimal runtime graph for orchestrating autonomous agents."""

    def __init__(self):
        self.nodes: List[ExecutionNode] = []

    def add_node(self, name: str, metadata: Optional[Dict[str, object]] = None) -> ExecutionNode:
        node = ExecutionNode(name=name, metadata=metadata or {})
        self.nodes.append(node)
        return node

    def mark_success(self, name: str) -> None:
        self._find(name).status = "success"

    def mark_running(self, name: str) -> None:
        node = self._find(name)
        node.status = "running"
        node.attempts += 1

    def mark_failed(self, name: str, error: Optional[str] = None) -> None:
        node = self._find(name)
        node.status = "failed"
        if error is not None:
            node.metadata["error"] = error

    def _find(self, name: str) -> ExecutionNode:
        for node in self.nodes:
            if node.name == name:
                return node
        raise KeyError(f"Unknown execution node: {name}")

    def snapshot(self) -> List[Dict[str, object]]:
        return [
            {
                "name": node.name,
                "status": node.status,
                "attempts": node.attempts,
                "metadata": node.metadata,
            }
            for node in self.nodes
        ]
