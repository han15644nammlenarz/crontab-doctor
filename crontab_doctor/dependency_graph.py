"""Dependency graph: detect ordering and overlap relationships between named cron jobs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .next_run import next_runs
from .parser import ParseError, parse_expression


@dataclass
class JobNode:
    name: str
    expression: str
    depends_on: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"JobNode(name={self.name!r}, expression={self.expression!r}, depends_on={self.depends_on!r})"


@dataclass
class GraphEdge:
    source: str
    target: str
    kind: str  # 'depends_on' | 'overlaps'

    def __repr__(self) -> str:  # pragma: no cover
        return f"GraphEdge({self.source!r} -[{self.kind}]-> {self.target!r})"


@dataclass
class GraphResult:
    nodes: List[JobNode]
    edges: List[GraphEdge]
    cycles: List[List[str]]
    errors: List[str]

    def summary(self) -> str:
        parts = [f"{len(self.nodes)} job(s), {len(self.edges)} edge(s)"]
        if self.cycles:
            parts.append(f"{len(self.cycles)} cycle(s) detected")
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        return "; ".join(parts)


def _detect_cycles(nodes: List[JobNode]) -> List[List[str]]:
    """Return list of cycles found in dependency edges using DFS."""
    adj: Dict[str, List[str]] = {n.name: list(n.depends_on) for n in nodes}
    visited: Dict[str, int] = {}  # 0=unvisited,1=in-stack,2=done
    cycles: List[List[str]] = []

    def dfs(node: str, path: List[str]) -> None:
        visited[node] = 1
        path.append(node)
        for neighbour in adj.get(node, []):
            if visited.get(neighbour) == 1:
                cycle_start = path.index(neighbour)
                cycles.append(list(path[cycle_start:]))
            elif visited.get(neighbour, 0) == 0:
                dfs(neighbour, path)
        path.pop()
        visited[node] = 2

    for n in adj:
        if visited.get(n, 0) == 0:
            dfs(n, [])
    return cycles


def _jobs_overlap(expr_a: str, expr_b: str, window: int = 5) -> bool:
    """Return True if the next *window* runs of both expressions share any timestamp."""
    try:
        runs_a = set(next_runs(expr_a, n=window))
        runs_b = set(next_runs(expr_b, n=window))
        return bool(runs_a & runs_b)
    except Exception:
        return False


def build_graph(jobs: List[JobNode], detect_overlaps: bool = True) -> GraphResult:
    """Build a dependency/overlap graph for the supplied job nodes."""
    errors: List[str] = []
    valid_names = {j.name for j in jobs}

    for job in jobs:
        try:
            parse_expression(job.expression)
        except ParseError as exc:
            errors.append(f"[{job.name}] invalid expression: {exc}")
        for dep in job.depends_on:
            if dep not in valid_names:
                errors.append(f"[{job.name}] unknown dependency: {dep!r}")

    edges: List[GraphEdge] = []
    for job in jobs:
        for dep in job.depends_on:
            if dep in valid_names:
                edges.append(GraphEdge(source=job.name, target=dep, kind="depends_on"))

    if detect_overlaps:
        names = [j.name for j in jobs]
        expr_map = {j.name: j.expression for j in jobs}
        for i in range(len(names)):
            for k in range(i + 1, len(names)):
                a, b = names[i], names[k]
                if _jobs_overlap(expr_map[a], expr_map[b]):
                    edges.append(GraphEdge(source=a, target=b, kind="overlaps"))

    cycles = _detect_cycles(jobs)
    return GraphResult(nodes=list(jobs), edges=edges, cycles=cycles, errors=errors)
