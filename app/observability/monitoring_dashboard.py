"""Render a local HTML monitoring dashboard from a dashboard snapshot."""

from html import escape
import json
from pathlib import Path
from typing import Any

from app.observability.dashboard_snapshot import DEFAULT_DASHBOARD_SNAPSHOT_PATH

DEFAULT_MONITORING_DASHBOARD_PATH = Path("reports/monitoring/dashboard.html")


class MonitoringDashboardError(ValueError):
    """Raised when a monitoring dashboard cannot be rendered."""


def load_dashboard_snapshot(path: Path) -> dict[str, Any]:
    """Load a dashboard snapshot JSON file."""
    if not path.is_file():
        raise MonitoringDashboardError(f"Dashboard snapshot file not found: {path}")
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MonitoringDashboardError(f"Invalid dashboard snapshot JSON: {path}") from exc
    if not isinstance(snapshot, dict):
        raise MonitoringDashboardError("Dashboard snapshot must be a JSON object.")
    return snapshot


def render_monitoring_dashboard(snapshot: dict[str, Any]) -> str:
    """Render a static local HTML monitoring dashboard."""
    cards = snapshot.get("cards")
    distributions = snapshot.get("distributions")
    freshness = snapshot.get("report_freshness")
    if not isinstance(cards, dict):
        raise MonitoringDashboardError("Dashboard snapshot is missing cards.")
    if not isinstance(distributions, dict):
        distributions = {}
    if not isinstance(freshness, dict):
        freshness = {}

    requests = _dict(cards.get("requests"))
    latency = _dict(cards.get("latency"))
    alerts = _dict(cards.get("alerts"))
    drift = _dict(cards.get("drift"))
    telemetry = _dict(cards.get("telemetry_quality"))
    prediction_distribution = _dict(distributions.get("prediction_distribution"))
    probability_distribution = _dict(distributions.get("probability_distribution"))
    drifted_features = _list(distributions.get("drifted_features"))

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>ModelOpsLab Monitoring Dashboard</title>",
            f"  <style>{_dashboard_css()}</style>",
            "</head>",
            "<body>",
            '  <main class="dashboard-shell">',
            '    <section class="dashboard-header">',
            "      <div>",
            "        <p>ModelOpsLab</p>",
            "        <h1>Monitoring Dashboard</h1>",
            f"        <span>Generated at {_text(snapshot.get('generated_at'))}</span>",
            "      </div>",
            f'      <div class="status status-{_status_class(snapshot.get("overall_status"))}">{_text(snapshot.get("overall_status", "unknown"))}</div>',
            "    </section>",
            '    <section class="card-grid" aria-label="Monitoring summary cards">',
            _metric_card(
                "Requests",
                _format_int(requests.get("request_count")),
                [
                    ("Success", _format_int(requests.get("success_count"))),
                    ("Failures", _format_int(requests.get("failure_count"))),
                    ("Failure rate", _format_rate(requests.get("failure_rate"))),
                ],
            ),
            _metric_card(
                "Latency",
                f'{_format_number(latency.get("p95"))} ms',
                [
                    ("Average", f'{_format_number(latency.get("average"))} ms'),
                    ("p99", f'{_format_number(latency.get("p99"))} ms'),
                    ("Count", _format_int(latency.get("count"))),
                ],
            ),
            _metric_card(
                "Alerts",
                _format_int(alerts.get("active_alert_count")),
                [
                    ("Status", _text(alerts.get("overall_status", "unknown"))),
                    (
                        "Triggered",
                        _comma_list(_list(alerts.get("triggered_alert_names"))),
                    ),
                ],
            ),
            _metric_card(
                "Drift",
                _text(drift.get("overall_status", "unknown")),
                [
                    ("Drifted features", _format_int(drift.get("drifted_feature_count"))),
                    ("Reference rows", _format_int(drift.get("reference_row_count"))),
                    ("Inference rows", _format_int(drift.get("inference_row_count"))),
                ],
            ),
            _metric_card(
                "Telemetry Quality",
                _format_int(telemetry.get("raw_event_count")),
                [
                    ("Skipped events", _format_int(telemetry.get("skipped_event_count"))),
                    ("Feature events", _format_int(telemetry.get("feature_event_count"))),
                ],
            ),
            "    </section>",
            '    <section class="dashboard-section">',
            "      <h2>Prediction Distribution</h2>",
            _bar_list(prediction_distribution),
            "    </section>",
            '    <section class="dashboard-section">',
            "      <h2>Probability Distribution</h2>",
            _probability_distribution(probability_distribution),
            "    </section>",
            '    <section class="dashboard-section">',
            "      <h2>Drifted Features</h2>",
            _pill_list(drifted_features),
            "    </section>",
            '    <section class="dashboard-section">',
            "      <h2>Report Freshness</h2>",
            _freshness_table(freshness),
            "    </section>",
            "  </main>",
            "</body>",
            "</html>",
        ]
    )


def save_monitoring_dashboard(
    html: str,
    output_path: Path = DEFAULT_MONITORING_DASHBOARD_PATH,
) -> None:
    """Persist rendered monitoring dashboard HTML."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def build_and_save_monitoring_dashboard(
    *,
    snapshot_path: Path = DEFAULT_DASHBOARD_SNAPSHOT_PATH,
    output_path: Path = DEFAULT_MONITORING_DASHBOARD_PATH,
) -> str:
    """Load a dashboard snapshot, render the dashboard, and persist it."""
    html = render_monitoring_dashboard(load_dashboard_snapshot(snapshot_path))
    save_monitoring_dashboard(html, output_path)
    return html


def _metric_card(title: str, value: str, rows: list[tuple[str, str]]) -> str:
    row_html = "\n".join(
        f'        <li><span>{escape(label)}</span><strong>{escape(value)}</strong></li>'
        for label, value in rows
    )
    return "\n".join(
        [
            '      <article class="metric-card">',
            f"        <h2>{escape(title)}</h2>",
            f'        <div class="metric-value">{escape(value)}</div>',
            f"        <ul>{row_html}</ul>",
            "      </article>",
        ]
    )


def _bar_list(distribution: dict[str, Any]) -> str:
    if not distribution:
        return '<p class="empty-state">No prediction distribution available.</p>'
    total = sum(_numeric(value) for value in distribution.values())
    rows = []
    for label, value in sorted(distribution.items()):
        numeric_value = _numeric(value)
        width = 0 if total == 0 else round((numeric_value / total) * 100, 2)
        rows.append(
            "\n".join(
                [
                    '      <div class="bar-row">',
                    f"        <span>{_text(label)}</span>",
                    '        <div class="bar-track">',
                    f'          <div class="bar-fill" style="width: {width}%"></div>',
                    "        </div>",
                    f"        <strong>{_format_number(numeric_value)}</strong>",
                    "      </div>",
                ]
            )
        )
    return "\n".join(rows)


def _probability_distribution(distribution: dict[str, Any]) -> str:
    buckets = distribution.get("buckets")
    if not isinstance(buckets, dict) or not buckets:
        return '<p class="empty-state">No probability buckets available.</p>'
    summary = [
        ("Count", _format_int(distribution.get("count"))),
        ("Average", _format_number(distribution.get("average"))),
        ("Min", _format_number(distribution.get("min"))),
        ("Max", _format_number(distribution.get("max"))),
    ]
    return "\n".join(
        [
            '<div class="compact-summary">',
            *[
                f"<span><strong>{escape(label)}</strong>{escape(value)}</span>"
                for label, value in summary
            ],
            "</div>",
            _bar_list(buckets),
        ]
    )


def _pill_list(values: list[Any]) -> str:
    if not values:
        return '<p class="empty-state">No drifted features reported.</p>'
    items = "\n".join(f"        <li>{_text(value)}</li>" for value in values)
    return f'      <ul class="pill-list">\n{items}\n      </ul>'


def _freshness_table(freshness: dict[str, Any]) -> str:
    if not freshness:
        return '<p class="empty-state">No freshness metadata available.</p>'
    rows = "\n".join(
        [
            "        <tr>"
            f"<th>{escape(str(key).replace('_', ' '))}</th>"
            f"<td>{_text(value)}</td>"
            "</tr>"
            for key, value in sorted(freshness.items())
        ]
    )
    return f'      <table class="freshness-table"><tbody>\n{rows}\n      </tbody></table>'


def _comma_list(values: list[Any]) -> str:
    if not values:
        return "None"
    return ", ".join(str(value) for value in values)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _numeric(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _format_int(value: Any) -> str:
    if isinstance(value, (int, float)):
        return str(int(value))
    return "0"


def _format_number(value: Any) -> str:
    if not isinstance(value, (int, float)):
        return "0"
    formatted = f"{float(value):.3f}".rstrip("0").rstrip(".")
    return formatted or "0"


def _format_rate(value: Any) -> str:
    if not isinstance(value, (int, float)):
        return "0%"
    return f"{float(value) * 100:.2f}%"


def _text(value: Any) -> str:
    if value is None:
        return ""
    return escape(str(value))


def _status_class(value: Any) -> str:
    status = str(value or "unknown").lower().replace("_", "-")
    allowed = {"ok", "alerting", "drift-detected", "insufficient-data", "unknown"}
    return status if status in allowed else "unknown"


def _dashboard_css() -> str:
    return """
:root {
  color-scheme: light;
  --bg: #f4f6f8;
  --panel: #ffffff;
  --text: #17202a;
  --muted: #627386;
  --line: #d9e0e7;
  --accent: #1f7a8c;
  --accent-strong: #145466;
  --warn: #b25b00;
  --danger: #a13d3d;
  --ok: #26734d;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: Arial, Helvetica, sans-serif;
}
.dashboard-shell {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 32px 0;
}
.dashboard-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}
.dashboard-header p {
  margin: 0 0 6px;
  color: var(--accent-strong);
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
}
.dashboard-header h1 {
  margin: 0;
  font-size: 34px;
  line-height: 1.1;
}
.dashboard-header span {
  display: block;
  margin-top: 8px;
  color: var(--muted);
  font-size: 14px;
}
.status {
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--panel);
  min-width: 140px;
  padding: 12px 16px;
  font-weight: 700;
  text-align: center;
}
.status-ok { color: var(--ok); }
.status-alerting,
.status-drift-detected { color: var(--danger); }
.status-insufficient-data,
.status-unknown { color: var(--warn); }
.card-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.metric-card,
.dashboard-section {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
}
.metric-card {
  min-height: 190px;
  padding: 16px;
}
.metric-card h2,
.dashboard-section h2 {
  margin: 0;
  font-size: 15px;
}
.metric-value {
  margin: 16px 0;
  min-height: 42px;
  font-size: 30px;
  font-weight: 700;
  line-height: 1.15;
  overflow-wrap: anywhere;
}
.metric-card ul {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.metric-card li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: var(--muted);
  font-size: 13px;
}
.metric-card li strong {
  color: var(--text);
  text-align: right;
  overflow-wrap: anywhere;
}
.dashboard-section {
  margin-top: 16px;
  padding: 18px;
}
.dashboard-section h2 {
  margin-bottom: 14px;
}
.bar-row {
  display: grid;
  grid-template-columns: minmax(90px, 160px) 1fr minmax(40px, 80px);
  align-items: center;
  gap: 12px;
  margin: 10px 0;
  font-size: 14px;
}
.bar-track {
  height: 12px;
  overflow: hidden;
  border-radius: 999px;
  background: #e8eef2;
}
.bar-fill {
  height: 100%;
  background: var(--accent);
}
.compact-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}
.compact-summary span {
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 10px;
  color: var(--muted);
}
.compact-summary strong {
  display: block;
  color: var(--text);
}
.pill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.pill-list li {
  border: 1px solid #b9d5dc;
  border-radius: 999px;
  background: #edf7f9;
  padding: 7px 10px;
  color: var(--accent-strong);
  font-size: 13px;
  font-weight: 700;
}
.freshness-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.freshness-table th,
.freshness-table td {
  border-top: 1px solid var(--line);
  padding: 10px 0;
  text-align: left;
  vertical-align: top;
}
.freshness-table th {
  width: 36%;
  color: var(--muted);
  font-weight: 600;
}
.empty-state {
  margin: 0;
  color: var(--muted);
}
@media (max-width: 1000px) {
  .card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .dashboard-shell {
    width: min(100% - 20px, 1180px);
    padding: 20px 0;
  }
  .dashboard-header {
    align-items: stretch;
    flex-direction: column;
  }
  .dashboard-header h1 { font-size: 28px; }
  .card-grid,
  .compact-summary { grid-template-columns: 1fr; }
  .bar-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
  .freshness-table th,
  .freshness-table td {
    display: block;
    width: 100%;
  }
  .freshness-table td {
    border-top: 0;
    padding-top: 0;
  }
}
""".strip()
