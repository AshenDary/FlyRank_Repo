"""Evaluate the finalized March model once on the sealed June slice."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.tree import DecisionTreeClassifier


ROOT = Path(__file__).resolve().parents[1]
EXTRACT_DIR = ROOT / "data" / "warehouse_extract"
DEV_FRAME = EXTRACT_DIR / "warehouse_model_frame.parquet"
SEALED_FACT = EXTRACT_DIR / "fact_content_daily_performance_2026_06.parquet"
DIM_CONTENT = EXTRACT_DIR / "dim_content.parquet"


FEATURES = [
    "ctr",
    "avg_position",
    "visible_valid_position",
    "ctr_gap_score",
    "log_impressions_90d",
    "days_since_last_update",
    "freshness_score",
]


def expected_ctr(position: pd.Series) -> pd.Series:
    return pd.Series(
        np.select(
            [position.between(0.01, 3), position.between(3.01, 10), position.between(10.01, 20)],
            [2.00, 1.00, 0.50],
            default=np.nan,
        ),
        index=position.index,
    )


def add_features(frame: pd.DataFrame, decision_date: str) -> pd.DataFrame:
    frame = frame.copy()
    frame["expected_ctr"] = expected_ctr(frame["avg_position"])
    frame["visible_valid_position"] = (
        frame["impressions_90d"].ge(300)
        & frame["avg_position"].gt(0)
        & frame["avg_position"].le(20)
    ).astype(int)
    frame["ctr_gap_score"] = (
        (frame["expected_ctr"] - frame["ctr"]) / frame["expected_ctr"]
    ).clip(lower=0, upper=1).fillna(0.0)
    frame["log_impressions_90d"] = np.log1p(frame["impressions_90d"])
    frame["days_since_last_update"] = frame["days_since_last_update"].clip(lower=0)
    frame["freshness_score"] = (frame["days_since_last_update"] / 180).clip(lower=0, upper=1)
    return frame


def aggregate_month(path: Path, content_path: Path, start: str, decision: str, end: str) -> pd.DataFrame:
    con = duckdb.connect()
    fact = str(path).replace("'", "''")
    content = str(content_path).replace("'", "''")
    query = f"""
    WITH daily AS (
        SELECT
            client_hash_id,
            content_hash_id,
            CAST(report_date AS DATE) AS report_date,
            COALESCE(gsc_impressions, 0)::DOUBLE AS impressions,
            COALESCE(gsc_clicks, 0)::DOUBLE AS clicks,
            gsc_avg_position AS avg_position
        FROM read_parquet('{fact}')
    ), grouped AS (
        SELECT
            client_hash_id AS client_id,
            content_hash_id AS content_id,
            SUM(CASE WHEN report_date <= DATE '{decision}' THEN impressions ELSE 0 END) AS impressions_90d,
            SUM(CASE WHEN report_date <= DATE '{decision}' THEN clicks ELSE 0 END) AS clicks_90d,
            SUM(CASE WHEN report_date > DATE '{decision}' THEN impressions ELSE 0 END) AS future_impressions,
            AVG(CASE WHEN report_date <= DATE '{decision}' THEN avg_position END) AS avg_position
        FROM daily
        GROUP BY 1, 2
    )
    SELECT
        g.*,
        CASE WHEN g.impressions_90d > 0 THEN g.clicks_90d / g.impressions_90d * 100 ELSE 0 END AS ctr,
        CASE WHEN g.impressions_90d >= 10 AND g.future_impressions < g.impressions_90d THEN 1 ELSE 0 END AS is_declining_label,
        GREATEST((DATE '{decision}' - COALESCE(c.last_optimized_date, c.content_updated_date, c.content_created_date, DATE '{decision}'))::DOUBLE, 0) AS days_since_last_update
    FROM grouped AS g
    LEFT JOIN read_parquet('{content}') AS c
      ON c.client_hash_id = g.client_id AND c.content_hash_id = g.content_id
    WHERE g.impressions_90d >= 10
    """
    frame = con.sql(query).df()
    frame = add_features(frame, decision)
    return frame


def clean(frame: pd.DataFrame, columns: list[str], medians: pd.Series | None = None) -> tuple[pd.DataFrame, pd.Series]:
    values = frame[columns].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    if medians is None:
        medians = values.median(numeric_only=True)
    return values.fillna(medians), medians


def main() -> None:
    march = pd.read_parquet(DEV_FRAME)
    june = aggregate_month(SEALED_FACT, DIM_CONTENT, "2026-06-01", "2026-06-15", "2026-07-01")
    march = add_features(march, "2026-03-15")
    X_train, medians = clean(march, FEATURES)
    X_test, _ = clean(june, FEATURES, medians)
    y_train = march["is_declining_label"].astype(int)
    y_test = june["is_declining_label"].astype(int)

    model = DecisionTreeClassifier(max_depth=4, min_samples_leaf=100, class_weight="balanced", random_state=42)
    model.fit(X_train, y_train)
    probability = model.predict_proba(X_test)[:, 1]
    ranking = june.assign(model_probability=probability).sort_values(
        ["model_probability", "impressions_90d", "ctr_gap_score", "content_id"],
        ascending=[False, False, False, True],
    )
    receipt = {
        "training_month": "2026-03",
        "sealed_test_month": "2026-06",
        "training_rows": int(len(march)),
        "training_clients": int(march["client_id"].nunique()),
        "test_rows": int(len(june)),
        "test_clients": int(june["client_id"].nunique()),
        "test_base_declining_rate": round(float(y_test.mean()), 4),
        "heldout_precision_at_10": round(float(y_test.loc[ranking.head(10).index].mean()), 4),
        "heldout_precision_at_50": round(float(y_test.loc[ranking.head(50).index].mean()), 4),
        "heldout_precision_at_500": round(float(y_test.loc[ranking.head(500).index].mean()), 4),
        "heldout_roc_auc": round(float(roc_auc_score(y_test, probability)), 4),
        "heldout_average_precision": round(float(average_precision_score(y_test, probability)), 4),
    }
    output = ROOT / "work" / "outputs" / "sealed_june_heldout_metrics.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()