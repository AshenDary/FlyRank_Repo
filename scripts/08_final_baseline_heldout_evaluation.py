"""Evaluate the unchanged baseline rule once on the sealed June slice."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
EXTRACT_DIR = ROOT / "data" / "warehouse_extract"
SEALED_FACT = EXTRACT_DIR / "fact_content_daily_performance_2026_06.parquet"
DIM_CONTENT = EXTRACT_DIR / "dim_content.parquet"


def aggregate_june() -> pd.DataFrame:
    con = duckdb.connect()
    fact = str(SEALED_FACT).replace("'", "''")
    content = str(DIM_CONTENT).replace("'", "''")
    query = f"""
    WITH daily AS (
        SELECT client_hash_id, content_hash_id, CAST(report_date AS DATE) AS report_date,
               COALESCE(gsc_impressions, 0)::DOUBLE AS impressions,
               COALESCE(gsc_clicks, 0)::DOUBLE AS clicks,
               gsc_avg_position AS avg_position
        FROM read_parquet('{fact}')
    ), grouped AS (
        SELECT client_hash_id AS client_id, content_hash_id AS content_id,
               SUM(CASE WHEN report_date <= DATE '2026-06-15' THEN impressions ELSE 0 END) AS impressions_90d,
               SUM(CASE WHEN report_date <= DATE '2026-06-15' THEN clicks ELSE 0 END) AS clicks_90d,
               SUM(CASE WHEN report_date > DATE '2026-06-15' THEN impressions ELSE 0 END) AS future_impressions,
               AVG(CASE WHEN report_date <= DATE '2026-06-15' THEN avg_position END) AS avg_position
        FROM daily GROUP BY 1, 2
    )
    SELECT g.*, CASE WHEN g.impressions_90d > 0 THEN g.clicks_90d / g.impressions_90d * 100 ELSE 0 END AS ctr,
           CASE WHEN g.impressions_90d >= 10 AND g.future_impressions < g.impressions_90d THEN 1 ELSE 0 END AS is_declining_label,
           GREATEST((DATE '2026-06-15' - COALESCE(c.last_optimized_date, c.content_updated_date, c.content_created_date, DATE '2026-06-15'))::DOUBLE, 0) AS days_since_last_update
    FROM grouped AS g
    LEFT JOIN read_parquet('{content}') AS c ON c.client_hash_id = g.client_id AND c.content_hash_id = g.content_id
    WHERE g.impressions_90d >= 10
    """
    frame = con.sql(query).df()
    frame["expected_ctr"] = np.select(
        [frame["avg_position"].between(0.01, 3), frame["avg_position"].between(3.01, 10), frame["avg_position"].between(10.01, 20)],
        [2.00, 1.00, 0.50], default=np.nan,
    )
    frame["visible_valid_position"] = (frame["impressions_90d"].ge(300) & frame["avg_position"].gt(0) & frame["avg_position"].le(20)).astype(int)
    frame["ctr_gap_score"] = ((frame["expected_ctr"] - frame["ctr"]) / frame["expected_ctr"]).clip(0, 1).fillna(0)
    frame["volume_score"] = np.log1p(frame["impressions_90d"]).rank(method="average", pct=True).fillna(0)
    frame["freshness_score"] = (frame["days_since_last_update"] / 180).clip(0, 1)
    frame["baseline_score"] = frame["visible_valid_position"] * 100 * (0.55 * frame["ctr_gap_score"] + 0.30 * frame["volume_score"] + 0.15 * frame["freshness_score"])
    return frame.sort_values(["baseline_score", "impressions_90d", "ctr_gap_score", "content_id"], ascending=[False, False, False, True])


def main() -> None:
    june = aggregate_june()
    y = june["is_declining_label"].astype(int)
    receipt = {
        "sealed_test_month": "2026-06",
        "rows_scored": int(len(june)),
        "clients": int(june["client_id"].nunique()),
        "base_declining_rate": round(float(y.mean()), 4),
        "baseline_precision_at_10": round(float(y.head(10).mean()), 4),
        "baseline_precision_at_50": round(float(y.head(50).mean()), 4),
        "baseline_precision_at_500": round(float(y.head(500).mean()), 4),
        "baseline_roc_auc": round(float(roc_auc_score(y, june["baseline_score"])), 4),
        "baseline_average_precision": round(float(average_precision_score(y, june["baseline_score"])), 4),
        "baseline_rule_inputs": ["avg_position", "ctr", "impressions_90d", "days_since_last_update"],
        "tuning_performed": False,
    }
    output = ROOT / "work" / "outputs" / "sealed_june_baseline_metrics.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()