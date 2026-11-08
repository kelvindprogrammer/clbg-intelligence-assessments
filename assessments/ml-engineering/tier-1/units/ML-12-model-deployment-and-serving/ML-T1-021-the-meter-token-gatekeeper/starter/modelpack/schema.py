class ValidationError(ValueError):
    """Raised by validate_record. `.errors` is a sorted list of (field, code) pairs."""

    def __init__(self, errors):
        self.errors = sorted(errors)
        super().__init__(str(self.errors))


def validate_record(record, schema):
    raise NotImplementedError("R1: collect every error as (field, code); codes: missing, unknown, type, range, category")
