class RolloutController:
    """One instance per rollout. `info` holds stages, label_lag, slo_ms and horizon. See README section D for obs."""

    def __init__(self, info):
        self.info = info
        self.last_reason = ""

    def decide(self, obs):
        raise NotImplementedError("R3: return 'hold', 'advance' or 'rollback'; set self.last_reason every call")
