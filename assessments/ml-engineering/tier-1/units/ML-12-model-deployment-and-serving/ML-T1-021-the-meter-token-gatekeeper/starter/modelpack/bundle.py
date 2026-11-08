class IntegrityError(Exception):
    """The file's checksum does not match its payload."""


class UnsupportedVersion(Exception):
    """The bundle's format_version is not one this code reads."""


def fit_bundle(records, y, schema, version="1.0.0"):
    raise NotImplementedError("R2: standardise numeric fields, one-hot categories, fit logistic regression, return a plain dict")


def encode(clean_record, bundle):
    raise NotImplementedError("R2: feature vector in the bundle's fixed feature_order")


def save_bundle(bundle, path):
    raise NotImplementedError("R3: write JSON {payload, sha256}; never pickle")


def load_bundle(path):
    raise NotImplementedError("R3: verify checksum then format_version; raise IntegrityError / UnsupportedVersion")


def predict(bundle, records):
    raise NotImplementedError("R4: one result dict per record; a bad record must not fail the batch")
