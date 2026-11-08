class DriftMonitor:
    """Streaming monitor. Your design: statistic, windowing, thresholds and seasonality handling."""

    def __init__(self, ref_batches, names, false_alarms_per_100d=1.0):
        raise NotImplementedError("R4: build the monitor from reference batches [(day, X), ...]")

    def update(self, day, X):
        raise NotImplementedError("R4: return the list of feature names in alarm on this day")
