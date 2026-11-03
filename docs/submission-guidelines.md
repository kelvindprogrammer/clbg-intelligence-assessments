# Submission Guidelines

These guidelines apply to every assessment unless its section I says otherwise.

## 1. Before you start

1. Register your attempt: open an **Assessment attempt** issue (see [assessment policy §5](assessment-policy.md#5-registering-an-attempt)).
2. Create a **private** GitHub repository named `clbg-<ASSESSMENT-ID>-<github-username>`, for example `clbg-DS-T1-006-adaeze-o`.
3. Copy into it the assessment's `starter/`, `tests/`, `resources/` and `submission-template/` contents, whichever exist. Keep the folder names unless the assessment says otherwise.
4. Make your first commit **before** writing any solution code, so your history shows where you started.

## 2. Repository requirements

Every submission repository must contain:

| File | Purpose |
|---|---|
| `README.md` | What this is, and how to set it up and run it **in 10 lines or fewer**, from a clean clone. |
| Dependency manifest | `requirements.txt` with bounded or pinned versions, or `pyproject.toml`/`uv.lock`, or `environment.yml`. For non-Python stacks, the equivalent. |
| The deliverables in section F | Code, notebooks, reports, artefacts. |
| `AI_USE_AND_SOURCES.md` | Your integrity declaration (see [assessment integrity](assessment-integrity.md)). |
| `.gitignore` | So that virtual environments, caches, large data and secrets stay out. |

**Never commit:**
- API keys, tokens or passwords. Use environment variables and a committed `.env.example` with **dummy** values.
- Real personal data.
- Large downloaded datasets. Document the download step instead.
- Model files larger than 50 MB, unless the assessment asks for them. Use the release assets or an external link the assessment allows.

If you accidentally commit a secret, **revoke it immediately**. Deleting the commit doesn't make the secret safe. Then tell your assessor.

## 3. Notebooks

- Notebooks must run top to bottom, without manual steps, in a fresh kernel ("Restart & Run All").
- Commit them **with outputs**, so assessors can read them without running them, and make sure the outputs match a fresh run.
- Put reusable logic in `.py` modules and import it. Notebooks are for analysis and narrative, not for hiding untested code.

## 4. Reproducibility checklist

- [ ] A clean clone, plus the setup steps in your README, reproduces every result you report.
- [ ] Random seeds are fixed and documented. Where results vary by seed, report the variation.
- [ ] Data download or generation is scripted.
- [ ] Hardware and run time are stated for any step slower than about 5 minutes.
- [ ] The tests pass: `pytest -q`.

## 5. Commit practice

- Commit early and often, with meaningful messages ("Handle ambiguous DD/MM dates", not "update").
- Your history is part of the evidence of independent work. Rewriting history to tidy it is fine. Squashing everything into one commit is not.

## 6. Submitting

1. Make sure the **acceptance criteria** in section G pass on a clean clone.
2. Add the CLBG assessor account (named in your attempt issue) as a **read-only collaborator**.
3. Comment on your attempt issue using the **Submission** template:
   - repository URL
   - the exact **commit SHA** being submitted (the assessor marks this commit only)
   - the assessment ID and version
   - any deviations from the specification, with reasons
4. Don't push to the submitted branch after submission until you get feedback. If you want to keep working, use another branch.

## 7. The technical defence

You'll be invited to a defence (5–10 minutes at Tier 1, 10–20 at Tier 2, 20–40 at Tier 3). Bring a machine with your repository ready to run. See [technical defence guide](../assessment-operations/oral-defense/technical-defence-guide.md) for what to expect and how to prepare.

## 8. After feedback

- **M / M−:** well done. With your consent, your project may be featured in a CLBG showcase. Consider polishing it into a portfolio piece (see the [member handbook](member-handbook.md#7-turning-assessments-into-portfolio-evidence)).
- **R:** address the listed deficiencies on a new branch, then resubmit in the same issue with a short change log.
- **N:** read the feedback, use the suggested preparation, and choose another assessment in the unit after the cooling-off period.
