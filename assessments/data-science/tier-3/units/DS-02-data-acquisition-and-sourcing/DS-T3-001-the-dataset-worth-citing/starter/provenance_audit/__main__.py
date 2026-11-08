"""python -m provenance_audit <catalogue_dir> --out findings.json   (R8)"""
import argparse
import json
from pathlib import Path

from . import audit, load_catalogue


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("catalogue_dir")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    findings = audit(load_catalogue(a.catalogue_dir))
    Path(a.out).write_text(json.dumps([{"dataset_id": f.dataset_id, "code": f.code} for f in findings], indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
