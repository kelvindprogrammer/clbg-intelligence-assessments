"""Fill in every function. See README section D.1.

A graph is a dict: step name -> {"fn": fn, "next": {label: target}, "retries": int (optional, default 0)}.
fn(state, ctx) -> (updates: dict, label: str). A target is a step name, END, or "HUMAN:<step>".
"""
END = "END"


def run_workflow(graph: dict, start: str, state: dict, ctx: dict, max_steps: int = 20, max_visits: int = 3) -> dict:
    raise NotImplementedError("R1-R3: run steps, route by label, retry transient failures, guard against loops")


def resume(graph: dict, checkpoint: dict, ctx: dict, updates: dict | None = None, **limits) -> dict:
    raise NotImplementedError("R4: continue a paused run from its checkpoint")


def validate_graph(graph: dict, start: str) -> list[str]:
    raise NotImplementedError("R5: static checks on the graph")


def build_order_desk(model, catalogue: dict) -> dict:
    raise NotImplementedError("R6: the order-desk graph")
