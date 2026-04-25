"""Tests for crontab_doctor.dependency_graph."""
import pytest

from crontab_doctor.dependency_graph import (
    GraphEdge,
    GraphResult,
    JobNode,
    _detect_cycles,
    _jobs_overlap,
    build_graph,
)


# ---------------------------------------------------------------------------
# JobNode / GraphResult helpers
# ---------------------------------------------------------------------------

def test_job_node_defaults():
    node = JobNode(name="backup", expression="0 2 * * *")
    assert node.depends_on == []


def test_graph_result_summary_no_issues():
    result = GraphResult(nodes=[], edges=[], cycles=[], errors=[])
    assert "0 job" in result.summary()


def test_graph_result_summary_with_cycles_and_errors():
    result = GraphResult(
        nodes=[],
        edges=[],
        cycles=[["a", "b"]],
        errors=["some error"],
    )
    assert "cycle" in result.summary()
    assert "error" in result.summary()


# ---------------------------------------------------------------------------
# _detect_cycles
# ---------------------------------------------------------------------------

def test_detect_cycles_no_cycle():
    nodes = [
        JobNode("a", "* * * * *", depends_on=["b"]),
        JobNode("b", "* * * * *"),
    ]
    assert _detect_cycles(nodes) == []


def test_detect_cycles_simple_cycle():
    nodes = [
        JobNode("a", "* * * * *", depends_on=["b"]),
        JobNode("b", "* * * * *", depends_on=["a"]),
    ]
    cycles = _detect_cycles(nodes)
    assert len(cycles) >= 1
    flat = [node for cycle in cycles for node in cycle]
    assert "a" in flat or "b" in flat


def test_detect_cycles_self_dependency():
    """A job that lists itself as a dependency should be detected as a cycle."""
    nodes = [
        JobNode("a", "* * * * *", depends_on=["a"]),
    ]
    cycles = _detect_cycles(nodes)
    assert len(cycles) >= 1
    flat = [node for cycle in cycles for node in cycle]
    assert "a" in flat


def test_detect_cycles_longer_chain():
    """Cycles spanning more than two nodes should be detected."""
    nodes = [
        JobNode("a", "* * * * *", depends_on=["b"]),
        JobNode("b", "* * * * *", depends_on=["c"]),
        JobNode("c", "* * * * *", depends_on=["a"]),
    ]
    cycles = _detect_cycles(nodes)
    assert len(cycles) >= 1
    flat = [node for cycle in cycles for node in cycle]
    assert any(name in flat for name in ("a", "b", "c"))


# ---------------------------------------------------------------------------
# _jobs_overlap
# ---------------------------------------------------------------------------

def test_jobs_overlap_same_expression():
    assert _jobs_overlap("* * * * *", "* * * * *") is True


def test_jobs_overlap_different_hours():
    # 2am vs 3am — should not share any run in next 5
    assert _jobs_overlap("0 2 * * *", "0 3 * * *") is False


def test_jobs_overlap_invalid_expression_returns_false():
    assert _jobs_overlap("not_valid", "* * * * *") is False


# ---------------------------------------------------------------------------
# build_graph
# ---------------------------------------------------------------------------

def test_build_graph_no_deps_no_overlaps():
    jobs = [
        JobNode("job_a", "0 1 * * *"),
        JobNode("job_b", "0 3 * * *"),
    ]
    result = build_graph(jobs, detect_overlaps=False)
    assert len(result.nodes) == 2
    assert result.edges == []
    assert result.cycles == []
    assert result.errors == []


def test_build_graph_records_dependency_edge():
    jobs = [
        JobNode("job_a", "0 2 * * *", depends_on=["job_b"]),
        JobNode("job_b", "0 1 * * *"),
    ]
    result = build_graph(jobs, detect_overlaps=False)
    dep_edges = [e for e in result.edges if e.kind == "depends_on"]
    assert len(dep_edges) == 1
    assert dep_edges[0].source == "job_a"
    assert dep_edges[0].target == "job_b"
