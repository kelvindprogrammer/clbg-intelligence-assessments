class ArtifactStore:
    def __init__(self, root):
        self.root = root

    def save(self, run):
        raise NotImplementedError("R5: write the run to the store, idempotently")

    def load(self, run_id):
        raise NotImplementedError("R5: read a run back")

    def verify(self, run_id):
        raise NotImplementedError("R5: detect tampering")

    def list_runs(self):
        raise NotImplementedError("R5: sorted run ids")


def diff_runs(a, b):
    raise NotImplementedError("R6: explain why two runs differ")
