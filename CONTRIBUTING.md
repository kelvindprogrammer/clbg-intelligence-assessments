# Contributing

Thank you for helping build CLBG's assessment infrastructure. It only stays excellent if members keep improving it.

## Ways to contribute

| Contribution | How |
|---|---|
| Report an ambiguity, error or broken link in an assessment | Open an **Assessment feedback** issue |
| Fix a typo or link | Pull request (a patch version bump in `metadata.yaml`) |
| Improve starter code, tests or tooling | Pull request with tests |
| Propose a new assessment | Open a **New assessment proposal** issue first, then follow the [authoring guide](docs/contributing/AUTHORING_GUIDE.md) |
| Join the review panel | Reach Tier 2 or above in a subtrack and ask the subtrack lead |

## Ground rules

1. **Never commit confidential assessor material** (reference solutions, hidden tests, marking notes). These belong in the private assessor kit.
2. **Never commit secrets or real personal data** (see [SECURITY.md](SECURITY.md)).
3. **Keep generated files generated.** Run `python tools/catalogue-generator/build_catalogue.py` instead of editing `CATALOGUE.md` or the index pages by hand.
4. **Every assessment change updates `metadata.yaml`**: the version and the changelog.
5. Follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Local checks before a PR

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-ci.txt
python tools/assessment-validator/validate.py
python tools/test-runner/run_tests.py
python tools/dataset-validator/validate_datasets.py
python tools/catalogue-generator/build_catalogue.py
python tools/repository-checker/check_links.py
```

## Review

- Any change to an assessment needs one reviewer from that subtrack. **New** Tier 3 assessments and Signature Challenges need two reviewers, at least one independent of the author.
- New assessments must include a completed [quality scorecard](docs/assessment-quality-scorecard.md) in the PR description.
- The matching assessor-kit entry must be merged before the public assessment can be marked `reviewed`.

## Licensing of contributions

By contributing, you agree that code is licensed under MIT and content (documentation, assessment text, synthetic datasets) under CC BY 4.0, as described in [LICENSE](LICENSE).
