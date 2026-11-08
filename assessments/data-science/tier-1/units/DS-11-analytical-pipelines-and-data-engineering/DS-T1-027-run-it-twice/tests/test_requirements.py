"""Public requirement tests (a sample; assessors run a hidden suite on freshly generated drops)."""
import pytest

from conftest import DATA, DROPS

import levyload as ll

COLS = {"COL-001", "COL-002"}


@pytest.mark.parametrize("text,kobo", [("12500", 1250000), ("12,500.00", 1250000), ("N12,500", 1250000),
                                       ("₦1,234.50", 123450), ("12500.5", 1250050), (" 7.05 ", 705)])
def test_r1_amounts_accepted(text, kobo):
    assert ll.parse_amount(text) == kobo


@pytest.mark.parametrize("text", ["", "abc", "-500", "0", "12.345.6", "12.345", "1,23,456", "N", None])
def test_r1_amounts_rejected(text):
    assert ll.parse_amount(text) is None


def test_r2_dates():
    assert ll.parse_date("2026-03-02") == "2026-03-02" and ll.parse_date("02/03/2026") == "2026-03-02"
    for bad in ["2026-13-01", "31/02/2026", "02-03-2026", "2026/03/02", "", "2/3/2026"]:
        assert ll.parse_date(bad) is None


def test_r3_validate_row_order_of_checks():
    ok = {"txn_id": " T1 ", "collector_id": "COL-001", "paid_on": "02/03/2026", "amount": "N1,000"}
    clean, why = ll.validate_row(ok, COLS)
    assert why is None and clean == {"txn_id": "T1", "collector_id": "COL-001", "paid_on": "2026-03-02", "amount_kobo": 100000}
    assert ll.validate_row({**ok, "txn_id": " "}, COLS)[1] == "missing_field"
    assert ll.validate_row({**ok, "amount": "x", "paid_on": "bad", "collector_id": "NOPE"}, COLS)[1] == "bad_amount"
    assert ll.validate_row({**ok, "paid_on": "bad", "collector_id": "NOPE"}, COLS)[1] == "bad_date"
    assert ll.validate_row({**ok, "collector_id": "NOPE"}, COLS)[1] == "unknown_collector"


def test_r4_read_drop_handles_bom_case_and_order():
    rows = ll.read_drop(DROPS / "levies_2026-03-04.csv")    # shuffled column order
    assert set(rows[0][1]) == {"txn_id", "collector_id", "paid_on", "amount"} and rows[0][0] == 2
    rows = ll.read_drop(DROPS / "levies_2026-03-06.csv")    # BOM
    assert "txn_id" in rows[0][1]
    assert all(r[1]["txn_id"] is not None for r in rows)


def _load_one(conn, name="levies_2026-03-02.csv"):
    ll.init_db(conn)
    cols = ll.load_collectors(DATA / "collectors.csv")
    return ll.load_file(conn, DROPS / name, cols), cols


def test_r5_schema_tables(conn):
    ll.init_db(conn); ll.init_db(conn)
    names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"levies", "quarantine", "load_log"} <= names
    pk = [r[1] for r in conn.execute("PRAGMA table_info(levies)") if r[5]]
    assert pk == ["txn_id"]


def test_r6_counts_add_up_and_files_are_idempotent(conn):
    res, cols = _load_one(conn)
    assert res.rows_in == res.loaded + res.rejected + res.duplicates and res.loaded > 100 and res.rejected > 5
    n = conn.execute("SELECT COUNT(*) FROM levies").fetchone()[0]
    again = ll.load_file(conn, DROPS / "levies_2026-03-02.csv", cols)
    assert again.skipped and (again.rows_in, again.loaded) == (res.rows_in, res.loaded)
    assert conn.execute("SELECT COUNT(*) FROM levies").fetchone()[0] == n
    assert conn.execute("SELECT COUNT(*) FROM load_log").fetchone()[0] == 1


def test_r6_failure_rolls_back_everything(conn):
    ll.init_db(conn)
    cols = ll.load_collectors(DATA / "collectors.csv")
    with pytest.raises(RuntimeError):
        ll.load_file(conn, DROPS / "levies_2026-03-02.csv", cols, fail_after=50)
    for t in ["levies", "quarantine", "load_log"]:
        assert conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] == 0
    assert ll.load_file(conn, DROPS / "levies_2026-03-02.csv", cols).loaded > 100


def test_r6_first_value_wins_on_conflicts(conn, tmp_path):
    ll.init_db(conn)
    f = tmp_path / "a.csv"
    f.write_text("txn_id,collector_id,paid_on,amount\nT1,COL-001,2026-03-02,100\nT1,COL-001,2026-03-02,100\nT1,COL-001,2026-03-02,200\n")
    r = ll.load_file(conn, f, {"COL-001"})
    assert (r.rows_in, r.loaded, r.duplicates, r.rejected) == (3, 1, 1, 1)
    assert conn.execute("SELECT amount_kobo FROM levies").fetchone()[0] == 10000
    assert conn.execute("SELECT reason FROM quarantine").fetchone()[0] == "conflicting_duplicate"


def test_r7_load_all_and_invariants(conn):
    ll.init_db(conn)
    cols = ll.load_collectors(DATA / "collectors.csv")
    res = ll.load_all(conn, DROPS, cols)
    assert [r.file for r in res] == sorted(r.file for r in res) and len(res) == 6
    assert ll.check_invariants(conn) == []
    assert sum(r.duplicates for r in res) > 30
    conn.execute("DELETE FROM levies WHERE rowid IN (SELECT rowid FROM levies LIMIT 3)")
    assert len(ll.check_invariants(conn)) >= 1
