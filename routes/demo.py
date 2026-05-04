from flask import Blueprint, render_template

from services.demo_logistics import build_demo

demo_bp = Blueprint("demo", __name__, url_prefix="/demo")


@demo_bp.route("/logistics-kpi")
def logistics_kpi():
    """Standalone Plotly demo dashboard.

    The template does NOT extend base.html — the demo is meant to look
    like a real internal app, not another portfolio page.
    """
    payload = build_demo()
    return render_template(
        "demo/logistics_kpi.html",
        kpis=payload["kpis"],
        figures=payload["figures"],
        meta=payload["meta"],
    )
