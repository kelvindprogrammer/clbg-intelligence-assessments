"""Contract tests: these pass on the unmodified starter."""
import hashlib
import inspect
import json

import pandas as pd
import pytest

from conftest import INBOX, REF

pytestmark = pytest.mark.contract

INBOX_SHA256 = "8daa8fd6216b234eab7c7cc9b71a8a195104f05d5c2ff787604a7c6c8ddc0ec8"


def test_inbox_unmodified():
    h = hashlib.sha256()
    for f in sorted(p for p in INBOX.rglob("*") if p.is_file()):
        h.update(f.relative_to(INBOX).as_posix().encode())
        h.update(f.read_bytes().replace(chr(13).encode() + chr(10).encode(), chr(10).encode()))
    assert h.hexdigest() == INBOX_SHA256, "resources/inbox has been modified. Restore the original deliveries."


def test_twenty_deliveries_with_manifests():
    days = sorted(p.name for p in INBOX.iterdir() if p.is_dir())
    assert len(days) == 20 and days[0] == "2026-06-01" and days[-1] == "2026-06-20"
    for d in days:
        m = json.loads((INBOX / d / "manifest.json").read_text(encoding="utf-8"))
        assert m["business_date"] == d and (INBOX / d / m["file"]).is_file()


def test_reference_files():
    agents = pd.read_csv(REF / "agents.csv", dtype=str)
    assert len(agents) == 150 and agents["agent_id"].is_unique
    hol = pd.read_csv(REF / "public_holidays.csv", dtype=str)
    assert "2026-06-12" in set(hol["date"])


def test_public_api():
    import feedguard
    assert feedguard.LEDGER_COLUMNS == ["business_date", "status", "n_rows", "n_accepted", "n_quarantined", "findings"]
    assert list(inspect.signature(feedguard.process_inbox).parameters) == [
        "inbox", "out", "contract_path", "agents_path", "holidays_path"]
