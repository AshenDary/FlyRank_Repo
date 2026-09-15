"""Extract the FlyRank warehouse and build a March-only modeling frame."""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
EXTRACT_DIR = ROOT / "data" / "warehouse_extract"
HF_ROOT = "hf://datasets/FlyRank/internship-warehouse"
DEV_MONTH = "2026-03"
SEALED_MONTH = "2026-06"


def relation(path: str) -> str:
    return f"read_parquet('{HF_ROOT}/{path}')"


def local_path(name: str) -> Path:
    return EXTRACT_DIR / f"{name}.parquet"


def extract(con: duckdb.DuckDBPyConnection, name: str, source: str) -> dict[str, object]:
    destination = local_path(name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    escaped_destination = str(destination).replace("'", "''")
    con.execute(
        f"COPY (SELECT * FROM {source}) TO '{escaped_destination}' "
        "(FORMAT PARQUET, COMPRESSION ZSTD)"
    )
    row_count = con.sql(f"SELECT COUNT(*) FROM read_parquet('{escaped_destination}')").fetchone()[0]
    return {
        "name": name,
        "rows": int(row_count),
        "bytes": destination.stat().st_size,
        "path": str(destination.relative_to(ROOT)),
    }


def build_model_frame(con: duckdb.DuckDBPyConnection) -> dict[str, object]:
    dev = relation(f"fact_content_daily_performance/month={DEV_MONTH}/*.parquet")
    content = relation("dim_content.parquet")
    destination = local_path("warehouse_model_frame")
    escaped_destination = str(destination).replace("'", "''")

    # March 15 is the decision date. Features use March 1-15; the label compares
    # March 16-31 against the first half, with no June data involved.
    query = f"""
    COPY (
        WITH daily AS (
            SELECT
                client_hash_id,
                content_hash_id,
                CAST(report_date AS DATE) AS report_date,
                COALESCE(gsc_impressions, 0)::DOUBLE AS impressions,
                COALESCE(gsc_clicks, 0)::DOUBLE AS clicks,
                COALESCE(gsc_avg_position, NULL)::DOUBLE AS avg_position
            FROM {dev}
            WHERE report_date >= DATE '2026-03-01'
              AND report_date < DATE '2026-04-01'
        ),
        split AS (
            SELECT
                client_hash_id,
                content_hash_id,
                SUM(CASE WHEN report_date <= DATE '2026-03-15' THEN impressions ELSE 0 END) AS impressions_90d,
                SUM(CASE WHEN report_date <= DATE '2026-03-15' THEN clicks ELSE 0 END) AS clicks_90d,
                SUM(CASE WHEN report_date > DATE '2026-03-15' THEN impressions ELSE 0 END) AS future_impressions,
                SUM(CASE WHEN report_date > DATE '2026-03-15' THEN clicks ELSE 0 END) AS future_clicks,
                AVG(CASE WHEN report_date <= DATE '2026-03-15' THEN avg_position END) AS avg_position,
                COUNT(CASE WHEN report_date <= DATE '2026-03-15' AND impressions > 0 THEN 1 END) AS days_with_impressions
            FROM daily
            GROUP BY 1, 2
        ),
        enriched AS (
            SELECT
                s.client_hash_id AS client_id,
                s.content_hash_id AS content_id,
                s.impressions_90d,
                s.clicks_90d,
                0::DOUBLE AS sessions_90d,
                s.avg_position,
                s.days_with_impressions,
                c.content_type,
                c.main_intent,
                c.word_count,
                c.char_count,
                c.search_volume,
                c.competition,
                c.competition_level,
                c.cpc,
                c.provider_used,
                c.model_used,
                COALESCE(c.content_created_date, DATE '2026-03-15') AS content_created_date,
                COALESCE(c.last_optimized_date, c.content_updated_date, c.content_created_date, DATE '2026-03-15') AS last_optimized_date,
                CASE
                    WHEN s.impressions_90d > 0
                    THEN s.clicks_90d / s.impressions_90d * 100
                    ELSE 0
                END AS ctr,
                CASE
                    WHEN s.impressions_90d > 0 AND s.future_impressions > 0
                    THEN (s.future_impressions - s.impressions_90d) / s.impressions_90d
                    ELSE 0
                END AS trend_pct,
                CASE
                    WHEN s.impressions_90d >= 10 AND s.future_impressions < s.impressions_90d
                    THEN 1 ELSE 0
                END AS is_declining_label,
                CASE
                    WHEN s.impressions_90d >= 10 AND s.future_impressions < s.impressions_90d
                    THEN 'down' ELSE 'not_down'
                END AS trend_direction
            FROM split AS s
            LEFT JOIN {content} AS c
              USING (client_hash_id, content_hash_id)
        )
        SELECT
            *,
            CASE WHEN avg_position > 0 AND avg_position <= 20 AND impressions_90d >= 300 THEN 1 ELSE 0 END AS visible_valid_position,
            CASE
                WHEN avg_position > 0 AND avg_position <= 3 THEN 2.00
                WHEN avg_position > 3 AND avg_position <= 10 THEN 1.00
                WHEN avg_position > 10 AND avg_position <= 20 THEN 0.50
                ELSE NULL
            END AS expected_ctr,
            (DATE '2026-03-15' - content_created_date)::INTEGER AS content_age_days,
            CASE
                WHEN avg_position <= 3 AND avg_position > 0 THEN 'top_3'
                WHEN avg_position <= 10 AND avg_position > 0 THEN 'top_10'
                WHEN avg_position <= 20 AND avg_position > 0 THEN 'top_20'
                ELSE 'not_visible'
            END AS position_tier,
            CASE
                WHEN days_with_impressions >= 12 THEN 'high_activity'
                WHEN days_with_impressions >= 5 THEN 'medium_activity'
                ELSE 'low_activity'
            END AS freshness_tier,
            CASE
                WHEN impressions_90d >= 1000 THEN 'high'
                WHEN impressions_90d >= 100 THEN 'medium'
                ELSE 'low'
            END AS impression_tier,
            GREATEST((DATE '2026-03-15' - last_optimized_date)::DOUBLE, 0) AS days_since_last_update
        FROM enriched
        WHERE impressions_90d >= 10
    ) TO '{escaped_destination}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """
    con.execute(query)

    # Add the same engineered columns used by Weeks 5-7 in a second local SQL pass.
    staged = f"read_parquet('{escaped_destination}')"
    con.execute(
        f"""
        COPY (
            SELECT
                *,
                LEAST(GREATEST((expected_ctr - ctr) / NULLIF(expected_ctr, 0), 0), 1) AS ctr_gap_score,
                LN(1 + impressions_90d) AS log_impressions_90d,
                LEAST(GREATEST(days_since_last_update / 180, 0), 1) AS freshness_score
            FROM {staged}
        ) TO '{escaped_destination}.tmp' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )
    tmp_path = Path(f"{destination}.tmp")
    tmp_path.replace(destination)
    row_count = con.sql(f"SELECT COUNT(*) FROM read_parquet('{escaped_destination}')").fetchone()[0]
    base_rate = con.sql(
        f"SELECT AVG(is_declining_label) FROM read_parquet('{escaped_destination}')"
    ).fetchone()[0]
    return {
        "name": "warehouse_model_frame",
        "rows": int(row_count),
        "bytes": destination.stat().st_size,
        "base_rate": float(base_rate),
        "path": str(destination.relative_to(ROOT)),
    }


def main() -> None:
    token = os.environ.get("HF_TOKEN")
    assert token, "HF_TOKEN not set in this environment"
    assert (ROOT / ".gitignore").read_text().find("data/warehouse_extract/") >= 0

    con = duckdb.connect()
    con.execute(f"CREATE OR REPLACE SECRET hf (TYPE huggingface, TOKEN '{token}')")

    # This probe confirms the flat dimension path and the partitioned fact path.
    clients = relation("dim_clients.parquet")
    dev = relation(f"fact_content_daily_performance/month={DEV_MONTH}/*.parquet")
    assert con.sql(f"SELECT COUNT(*) FROM {clients}").fetchone()[0] == 104
    assert con.sql(f"SELECT COUNT(*) FROM {dev}").fetchone()[0] > 0

    extracts = [
        extract(con, "fact_content_daily_performance_2026_03", dev),
        extract(con, "fact_content_daily_performance_2026_06", relation(f"fact_content_daily_performance/month={SEALED_MONTH}/*.parquet")),
        extract(con, "dim_content", relation("dim_content.parquet")),
        extract(con, "dim_clients", clients),
        extract(con, "fact_content_query_90d", relation("fact_content_query_90d.parquet")),
    ]
    model_frame = build_model_frame(con)
    print(json.dumps({"extracts": extracts, "model_frame": model_frame}, indent=2))


if __name__ == "__main__":
    main()