"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and hostile inputs."""
import json
import math

import numpy as np
import pytest
from sklearn.metrics import roc_auc_score

import datagen
import modelpack as mp

S = datagen.SCHEMA
GOOD = {"token_amount_ngn": 5000.0, "kwh_registered": 52.0, "vends_last_30d": 4, "meter_type": "single_phase",
        "days_since_last_vend": 9.0}


def errs(rec):
    with pytest.raises(mp.ValidationError) as e:
        mp.validate_record(rec, S)
    return e.value.errors


def test_r1_valid_record_is_cleaned_and_ordered():
    out = mp.validate_record({**GOOD, "vends_last_30d": "4", "token_amount_ngn": " 5000 "}, S)
    assert list(out) == list(S) and out["vends_last_30d"] == 4 and isinstance(out["vends_last_30d"], int)
    assert out["token_amount_ngn"] == 5000.0


def test_r1_collects_all_errors_with_codes():
    bad = {**GOOD, "kwh_registered": -1, "meter_type": "solar", "extra": 1}
    del bad["days_since_last_vend"]
    assert errs(bad) == [("days_since_last_vend", "missing"), ("extra", "unknown"),
                         ("kwh_registered", "range"), ("meter_type", "category")]


def test_r1_type_traps():
    assert errs({**GOOD, "token_amount_ngn": True}) == [("token_amount_ngn", "type")]
    assert errs({**GOOD, "token_amount_ngn": "abc"}) == [("token_amount_ngn", "type")]
    assert errs({**GOOD, "vends_last_30d": 3.5}) == [("vends_last_30d", "type")]
    assert errs({**GOOD, "kwh_registered": float("nan")}) == [("kwh_registered", "range")]
    assert errs({**GOOD, "kwh_registered": "inf"}) == [("kwh_registered", "range")]
    assert errs({**GOOD, "meter_type": None}) == [("meter_type", "missing")]
    assert errs("not a dict") == [("<record>", "type")]


@pytest.fixture(scope="module")
def bundle():
    recs, y = datagen.make_vends(3000, seed=2026)
    return mp.fit_bundle(recs[:2000], y[:2000], S, version="1.2.0"), recs[2000:], y[2000:]


def test_r2_bundle_is_plain_json_and_quality(bundle):
    b, recs, y = bundle
    json.dumps(b)
    assert b["version"] == "1.2.0" and b["format_version"] == 1
    out = mp.predict(b, recs)
    assert roc_auc_score(y, [o["score"] for o in out]) > 0.75


def test_r2_encode_is_stable_and_uses_training_statistics(bundle):
    b, recs, y = bundle
    x = mp.encode(mp.validate_record(recs[0], S), b)
    assert x.shape == (len(b["weights"]),)
    assert np.allclose(x, mp.encode(mp.validate_record(dict(reversed(list(recs[0].items()))), S), b))


def test_r3_round_trip_and_tamper(bundle, tmp_path):
    b, recs, _ = bundle
    p = tmp_path / "m.json"
    mp.save_bundle(b, str(p))
    b2 = mp.load_bundle(str(p))
    assert [o["score"] for o in mp.predict(b2, recs[:50])] == [o["score"] for o in mp.predict(b, recs[:50])]
    d = json.loads(p.read_text())
    d["payload"]["weights"][0] += 0.001
    p.write_text(json.dumps(d))
    with pytest.raises(mp.IntegrityError):
        mp.load_bundle(str(p))


def test_r3_unsupported_version_is_reported(bundle, tmp_path):
    import hashlib
    b, _, _ = bundle
    payload = {**b, "format_version": 2}
    canon = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    p = tmp_path / "future.json"
    p.write_text(json.dumps({"payload": payload, "sha256": hashlib.sha256(canon.encode()).hexdigest()}))
    with pytest.raises(mp.UnsupportedVersion):
        mp.load_bundle(str(p))


def test_r3_file_is_not_a_pickle(bundle, tmp_path):
    p = tmp_path / "m.json"
    mp.save_bundle(bundle[0], str(p))
    d = json.loads(p.read_text())
    assert set(d) == {"payload", "sha256"} and len(d["sha256"]) == 64


def test_r4_isolates_bad_records_and_keeps_order(bundle):
    b, recs, _ = bundle
    batch = [recs[0], {**GOOD, "meter_type": "solar"}, recs[1], "junk"]
    out = mp.predict(b, batch)
    assert [o["ok"] for o in out] == [True, False, True, False]
    assert out[1]["errors"] == [["meter_type", "category"]] or out[1]["errors"] == [("meter_type", "category")]
    assert out[0]["model_version"] == "1.2.0" and 0.0 < out[0]["score"] < 1.0
    assert mp.predict(b, []) == []


def test_r4_score_does_not_depend_on_batch_and_is_stable_for_extremes(bundle):
    b, recs, _ = bundle
    single = mp.predict(b, [recs[3]])[0]["score"]
    assert single == mp.predict(b, recs[:10])[3]["score"]
    extreme = {**GOOD, "token_amount_ngn": 200000.0, "kwh_registered": 0.1, "vends_last_30d": 60}
    s = mp.predict(b, [extreme])[0]["score"]
    assert math.isfinite(s) and 0.0 <= s <= 1.0
