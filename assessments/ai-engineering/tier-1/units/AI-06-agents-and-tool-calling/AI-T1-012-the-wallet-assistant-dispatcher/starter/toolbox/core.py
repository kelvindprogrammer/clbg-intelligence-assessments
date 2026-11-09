"""Starter stubs for AI-T1-012. Implement R1-R5; see README section D."""
SENSITIVE_KEYS = ("bvn", "phone", "pin")


def validate_args(schema, args):
    raise NotImplementedError("R1: sorted list of error strings, empty when valid")


class ToolRegistry:
    def __init__(self):
        raise NotImplementedError("R2: store tools by name")

    def register(self, name, schema, fn, description):
        raise NotImplementedError("R2: add a tool; ValueError on a duplicate name")

    def describe(self):
        raise NotImplementedError("R2: one line per tool, sorted by name")

    def call(self, name, args):
        raise NotImplementedError("R2: validate, apply defaults, run, and never raise")


def parse_tool_call(text):
    raise NotImplementedError("R3: ('call', name, args) | ('final', text) | ('invalid', reason)")


def redact(obj, keys=SENSITIVE_KEYS):
    raise NotImplementedError("R4: replace values of sensitive keys by '***', recursively, without mutating")


def run_agent(model, registry, user_msg, max_steps=6, redact_keys=SENSITIVE_KEYS):
    raise NotImplementedError("R5: bounded loop over model.next, parse, call, record")
