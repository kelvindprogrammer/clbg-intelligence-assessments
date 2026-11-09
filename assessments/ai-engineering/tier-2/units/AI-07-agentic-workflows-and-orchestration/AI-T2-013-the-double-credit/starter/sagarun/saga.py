"""Fill in every function. See README section D.1. The defaults are a starting point, not a recommendation."""
from __future__ import annotations

DEFAULT_CFG = {
    "policy": {"max_attempts": 4, "base_delay": 1.0, "factor": 2.0, "max_delay": 8.0},
    "comp_attempts": 8,           # attempts allowed for each compensating call
    "approval_threshold": 500_000,
    "max_asks": 3,
    "idempotent": True,
}


def validate_plan(plan: list[dict], tools: dict) -> list[str]:
    raise NotImplementedError("R1: static plan validation")


def waves(plan: list[dict]) -> list[list[str]]:
    raise NotImplementedError("R2: layers of steps that can run in parallel")


def call_step(services, step: dict, run_id: str, policy: dict, clock, idempotent: bool = True) -> dict:
    raise NotImplementedError("R3: one step with idempotency key and retries")


def run_saga(services, plan: list[dict], request: dict, cfg: dict, clock, approver=None) -> dict:
    raise NotImplementedError("R4: execute by waves, ask for approval, compensate on failure")


def plan_with_repair(planner, request: dict, tools: dict, max_asks: int = 3) -> dict:
    raise NotImplementedError("R5: ask the planner until it produces a valid plan")


def violations(audit: dict, requests: list[dict], statuses: list[str]) -> list[str]:
    raise NotImplementedError("R6: compare the final world state with what each status promises")


def run_batch(services, planner, requests: list[dict], cfg: dict, clock_factory, approver=None) -> dict:
    raise NotImplementedError("R6: run all requests and summarise")
