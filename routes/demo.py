from flask import Blueprint, jsonify, render_template, request

from services.demo_logistics import build_demo, truck_detail

demo_bp = Blueprint("demo", __name__, url_prefix="/demo")

# Whitelist of allowed period filters (days). None = full history.
ALLOWED_PERIODS = {None, 30, 90, 180}


def _parse_period() -> int | None:
    raw = request.args.get("period")
    if not raw or raw == "all":
        return None
    try:
        days = int(raw)
    except (TypeError, ValueError):
        return None
    return days if days in ALLOWED_PERIODS else None


@demo_bp.route("/logistics-kpi")
def logistics_kpi():
    """Standalone Plotly demo dashboard.

    Server-rendered first paint with full history; subsequent filter
    changes hit the JSON API endpoints below without a page reload.
    """
    payload = build_demo(period_days=None)
    return render_template(
        "demo/logistics_kpi.html",
        kpis=payload["kpis"],
        figures=payload["figures"],
        meta=payload["meta"],
        trucks=payload["trucks"],
    )


@demo_bp.route("/logistics-kpi/api/figures")
def api_figures():
    """Re-aggregated KPIs + figures for a given period filter."""
    period = _parse_period()
    payload = build_demo(period_days=period)
    return jsonify({
        "kpis": payload["kpis"],
        "figures": payload["figures"],
        "trucks": payload["trucks"],
        "meta": payload["meta"],
    })


@demo_bp.route("/logistics-kpi/api/truck/<truck_id>")
def api_truck(truck_id: str):
    """Per-truck drill-down: stats, top routes, mini-figures, EU map."""
    period = _parse_period()
    detail = truck_detail(truck_id, period_days=period)
    if "error" in detail:
        return jsonify(detail), 404
    return jsonify(detail)
