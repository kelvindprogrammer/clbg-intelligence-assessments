# AI Engineering

> **Building reliable, secure software products on top of foundation models.**

AI engineers turn foundation models into **dependable software**. This subtrack assesses:
- model fundamentals;
- prompting and structured output;
- API and local-model integration;
- embeddings and retrieval;
- RAG, agents and orchestration;
- context and memory;
- multimodal systems;
- evaluation and observability;
- security and responsible AI;
- model adaptation;
- production architecture under cost and latency budgets.

**What sets AI Engineering apart from the other subtracks.** ML Engineering trains and operates models. AI Engineering **composes** models, tools, data and humans into applications, and proves they behave well. The hard parts are evaluation, reliability and security, not model training. That's why [AI-10 Evaluation](tier-2/README.md) and [AI-11 Security](tier-2/README.md) run through every tier. See the [competency framework](../../docs/competency-framework.md).

## How to use this subtrack

1. **Pick a tier.** [Tier 1](tier-1/README.md) · [Tier 2](tier-2/README.md) · [Tier 3](tier-3/README.md). See [tier definitions](../../docs/tier-definitions.md).
2. **Pick a unit** from the map below. There's no required order.
3. **Pick any assessment** in that unit and tier.
4. **Register, build, submit, defend.** See the [member handbook](../../docs/member-handbook.md).

**No paid API required.** Every assessment works with a local open-weight model (for example through Ollama or Hugging Face) or a provided deterministic mock. Hosted APIs, including free tiers, are optional. The tests run on the mock, so your results never depend on your budget.

**Security by default.** Never commit API keys. Agents and tools run with least privilege, sandboxed execution, and human approval for consequential actions. See [SECURITY.md](../../SECURITY.md).

**Typical tools:** Python (TypeScript where justified), FastAPI, Pydantic, Ollama / Hugging Face Transformers, sentence-transformers, FAISS, PostgreSQL + pgvector, SQLite, OpenTelemetry-style tracing, pytest, Docker.

<!-- CATALOGUE:START -->
<!-- CATALOGUE:END -->

## Capstones

See [capstones](capstones/README.md) once they're published, and the [cross-disciplinary challenges](../../cross-disciplinary/README.md).
