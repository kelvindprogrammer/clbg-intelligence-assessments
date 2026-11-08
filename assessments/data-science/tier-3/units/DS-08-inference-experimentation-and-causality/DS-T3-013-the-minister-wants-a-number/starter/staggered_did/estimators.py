"""Point estimators (R1-R3)."""


def twfe_att(df):
    """R1: coefficient on the treatment indicator in a two-way fixed-effects regression (balanced panel)."""
    raise NotImplementedError("R1: twfe_att")


def group_time_att(df, controls="never"):
    """R2: group-time average treatment effects ATT(g, t) with base period g-1."""
    raise NotImplementedError("R2: group_time_att")


def aggregate_att(gt, how="simple"):
    """R3: aggregate a group-time table: 'simple' (float), 'event' (DataFrame e, att) or 'cohort' (DataFrame g, att)."""
    raise NotImplementedError("R3: aggregate_att")
