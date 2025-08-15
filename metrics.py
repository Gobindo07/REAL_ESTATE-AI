import pandas as pd
import numpy as np

def add_metrics_and_rank(df: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """
    Adds underwriting metrics and a deal score to the dataframe.
    weights: dictionary with keys: cap, coc, noi, risk, growth, rrr
    """

    df = df.copy()

    # Avoid divide-by-zero
    df["NOI"] = (df["monthly_rent"] * (1 - df["vacancy_rate"])) - df["monthly_expenses"]

    df["cap_rate"] = df["NOI"] * 12 / df["price"]

    total_investment = df["price"] + df["rehab_cost"]
    df["cash_on_cash"] = (df["NOI"] * 12) / total_investment

    df["predicted_rent_growth"] = df.get("city_growth_rate", pd.Series([0] * len(df)))

    # Dummy risk score (lower is better)
    df["risk_score"] = np.where(df["risk_flags"].notna() & (df["risk_flags"] != ""),
                                1.0, 0.2)

    # Required Rate of Return pass/fail (dummy: pass if CoC > 8%)
    df["rrr_pass"] = (df["cash_on_cash"] > 0.08).astype(int)

    # Normalize weights
    total_weight = sum(weights.values()) if sum(weights.values()) > 0 else 1
    norm_w = {k: v / total_weight for k, v in weights.items()}

    # Calculate deal score (higher better)
    df["deal_score"] = (
        (df["cap_rate"] * norm_w["cap"]) +
        (df["cash_on_cash"] * norm_w["coc"]) +
        ((df["NOI"] / df["NOI"].max()) * norm_w["noi"]) +
        ((1 - df["risk_score"] / df["risk_score"].max()) * norm_w["risk"]) +
        ((df["predicted_rent_growth"] / df["predicted_rent_growth"].max()) * norm_w["growth"]) +
        (df["rrr_pass"] * norm_w["rrr"])
    )

    df.sort_values("deal_score", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df
