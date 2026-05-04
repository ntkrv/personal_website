"""Mock-data generator + Plotly figure builder for the public
"Logistics Cockpit" demo at /demo/logistics-kpi.

Everything is deterministic (single numpy seed) so the demo looks the
same on every page load. Heavy results are `lru_cache`d so the dataset
is generated exactly once per process and figures only re-render when
the period filter changes.

The dataset is intentionally small but coherent: trucks → trips →
planners → forwarders are all referentially consistent so the numbers
in the Fleet, Planning, and Forwarders tabs reconcile.
"""
from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache
from typing import Dict, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio


# ---------------------------------------------------------------------------
# Theme — applied to every figure so the cockpit stays visually coherent.
# ---------------------------------------------------------------------------

COLORS = {
    "bg": "#0f172a",          # slate-900
    "card": "#1a2332",        # slate-800-ish
    "grid": "#1f2937",        # slate-800
    "line": "#2c3a52",        # divider lines / country borders
    "text": "#e2e8f0",        # slate-200
    "muted": "#94a3b8",       # slate-400
    "amber": "#f59e0b",       # primary accent
    "amber_soft": "#fbbf24",  # amber-400
    "cyan": "#22d3ee",        # secondary accent
    "emerald": "#10b981",     # ok
    "rose": "#f43f5e",        # warn / late
    "violet": "#a78bfa",      # tertiary
}

TRUCK_MODELS = [
    "Volvo FH",
    "MAN TGX",
    "Mercedes Actros",
    "Scania R",
    "DAF XF",
    "Renault T",
]
MODEL_BASE_FUEL = {  # litres / 100km @ ~50% load
    "Volvo FH": 26.5,
    "MAN TGX": 27.2,
    "Mercedes Actros": 26.8,
    "Scania R": 25.9,
    "DAF XF": 27.5,
    "Renault T": 28.1,
}

PLANNERS = ["Anna K.", "Marek P.", "Lukas B.", "Sofia R."]
FORWARDERS = [
    "In-house fleet",
    "EuroFreight Logistics",
    "Trans-Continental EU",
    "RoadBridge Cargo",
    "Westline Hauliers",
]

EUROPEAN_HUBS = {
    "Berlin": (52.52, 13.40),
    "Warsaw": (52.23, 21.01),
    "Lyon": (45.76, 4.84),
    "Milan": (45.46, 9.19),
    "Madrid": (40.42, -3.70),
    "Brussels": (50.85, 4.35),
    "Amsterdam": (52.37, 4.90),
    "Munich": (48.14, 11.58),
    "Vienna": (48.21, 16.37),
    "Prague": (50.08, 14.43),
}

CO2_PER_LITRE_DIESEL_KG = 2.68  # well-to-wheel diesel coefficient


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    lat1, lat2 = np.radians(lat1), np.radians(lat2)
    dlat = lat2 - lat1
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return float(r * 2 * np.arcsin(np.sqrt(a)))


# ---------------------------------------------------------------------------
# Mock dataset
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _cached_dataset() -> Dict[str, pd.DataFrame]:
    return _generate_dataset()


def _filter_by_period(trips: pd.DataFrame, period_days: Optional[int]) -> pd.DataFrame:
    """Return rows from the last `period_days` days, or all rows if None."""
    if not period_days:
        return trips
    cutoff = trips["date"].max() - pd.Timedelta(days=period_days)
    return trips[trips["date"] >= cutoff]


def _generate_dataset(seed: int = 42) -> Dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)

    # --- Fleet ---
    n_trucks = 28
    trucks = pd.DataFrame({
        "truck_id": [f"T-{i:03d}" for i in range(1, n_trucks + 1)],
        "model": rng.choice(TRUCK_MODELS, size=n_trucks),
        "year": rng.integers(2018, 2025, size=n_trucks),
    })
    trucks["base_fuel"] = trucks["model"].map(MODEL_BASE_FUEL)
    # Per-truck wear factor — older + random aging hits efficiency.
    age = 2026 - trucks["year"]
    trucks["wear"] = 1 + (age * 0.012) + rng.normal(0, 0.025, n_trucks)

    # --- Trips: 6 months of daily routes ---
    end = date(2025, 12, 31)
    start = end - timedelta(days=180)
    days = pd.date_range(start, end, freq="D")

    rows = []
    hub_names = list(EUROPEAN_HUBS.keys())
    for d in days:
        # Fewer trips on weekends.
        n = rng.integers(14, 22) if d.weekday() < 5 else rng.integers(6, 11)
        active_trucks = rng.choice(trucks["truck_id"].values, size=n, replace=False)
        for truck_id in active_trucks:
            origin, dest = rng.choice(hub_names, size=2, replace=False)
            o_lat, o_lon = EUROPEAN_HUBS[origin]
            d_lat, d_lon = EUROPEAN_HUBS[dest]
            planned_km = _haversine_km(o_lat, o_lon, d_lat, d_lon) * rng.uniform(1.10, 1.25)
            actual_km = planned_km * rng.uniform(1.00, 1.07)
            empty_km = actual_km * rng.uniform(0.04, 0.30)
            on_time = bool(rng.random() < 0.86)
            idle_hours = rng.exponential(0.6) + (0 if on_time else rng.uniform(1.0, 4.0))
            tonnes = float(rng.uniform(8, 24))
            rows.append({
                "date": d,
                "truck_id": truck_id,
                "origin": origin,
                "destination": dest,
                "planned_km": planned_km,
                "actual_km": actual_km,
                "empty_km": empty_km,
                "loaded_km": actual_km - empty_km,
                "on_time": on_time,
                "idle_hours": idle_hours,
                "tonnes": tonnes,
                "planner": rng.choice(PLANNERS),
                "forwarder": rng.choice(FORWARDERS, p=[0.42, 0.18, 0.16, 0.14, 0.10]),
            })

    trips = pd.DataFrame(rows).merge(trucks, on="truck_id", how="left")

    # Fuel use: base fuel * wear * load factor + noise
    load_factor = 0.7 + (trips["tonnes"] / 24) * 0.6  # 0.7..1.3
    fuel_l_per_100km = trips["base_fuel"] * trips["wear"] * load_factor
    trips["fuel_l"] = (trips["actual_km"] / 100) * fuel_l_per_100km
    trips["co2_kg"] = trips["fuel_l"] * CO2_PER_LITRE_DIESEL_KG
    trips["fuel_l_per_100km"] = (trips["fuel_l"] / trips["actual_km"]) * 100

    # Per-trip cost: own fleet uses internal cost-per-km curve;
    # forwarders use a contract rate with variance.
    base_cpk = {
        "In-house fleet": 0.94,
        "EuroFreight Logistics": 1.08,
        "Trans-Continental EU": 1.12,
        "RoadBridge Cargo": 1.05,
        "Westline Hauliers": 1.18,
    }
    trips["cost_per_km_eur"] = trips["forwarder"].map(base_cpk) + rng.normal(0, 0.04, len(trips))
    trips["cost_eur"] = trips["cost_per_km_eur"] * trips["actual_km"]
    trips["claim"] = rng.random(len(trips)) < trips["forwarder"].map(
        {"In-house fleet": 0.005, "EuroFreight Logistics": 0.012,
         "Trans-Continental EU": 0.018, "RoadBridge Cargo": 0.010,
         "Westline Hauliers": 0.024}
    )

    return {"trucks": trucks, "trips": trips}


# ---------------------------------------------------------------------------
# Headline KPIs
# ---------------------------------------------------------------------------

def _compute_kpis(trips: pd.DataFrame) -> Dict[str, Dict[str, str]]:
    total_km = trips["actual_km"].sum()
    total_co2_t = trips["co2_kg"].sum() / 1000
    avg_fuel = (trips["fuel_l"].sum() / trips["actual_km"].sum()) * 100
    days_active = trips["date"].dt.date.nunique()
    fleet_size = trips["truck_id"].nunique()
    utilization = trips.groupby("truck_id")["date"].nunique().mean() / days_active

    empty_pct = trips["empty_km"].sum() / trips["actual_km"].sum() * 100
    avg_idle = trips["idle_hours"].mean()
    on_time_pct = trips["on_time"].mean() * 100
    n_routes = len(trips)

    forwarder_trips = trips[trips["forwarder"] != "In-house fleet"]
    forwarder_tonnes = forwarder_trips["tonnes"].sum()
    forwarder_cpk = (forwarder_trips["cost_eur"].sum()
                     / forwarder_trips["actual_km"].sum())
    forwarder_otp = forwarder_trips["on_time"].mean() * 100
    claim_rate = forwarder_trips["claim"].mean() * 100

    def _fmt(v, suffix=""):
        if v >= 1_000_000:
            return f"{v / 1_000_000:.1f}M{suffix}"
        if v >= 1_000:
            return f"{v / 1_000:.1f}k{suffix}"
        return f"{v:.1f}{suffix}"

    return {
        "fleet": {
            "Total distance": _fmt(total_km, " km"),
            "Avg consumption": f"{avg_fuel:.1f} L / 100km",
            "CO₂ emissions": f"{total_co2_t:,.0f} t",
            "Fleet utilization": f"{utilization * 100:.0f}%",
        },
        "planning": {
            "Empty kilometres": f"{empty_pct:.1f}%",
            "Avg idle / trip": f"{avg_idle:.1f} h",
            "On-time deliveries": f"{on_time_pct:.1f}%",
            "Routes planned": f"{n_routes:,}",
        },
        "forwarders": {
            "Sub-contracted tonnes": f"{forwarder_tonnes:,.0f} t",
            "Avg cost / km": f"€ {forwarder_cpk:.2f}",
            "Forwarder on-time": f"{forwarder_otp:.1f}%",
            "Claim rate": f"{claim_rate:.2f}%",
        },
    }


# ---------------------------------------------------------------------------
# Plotly figures
# ---------------------------------------------------------------------------

def _apply_layout(fig: go.Figure, height: int = 320, title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0.0, xanchor="left",
                   font=dict(size=14, color=COLORS["text"], family="Inter")),
        plot_bgcolor=COLORS["card"],
        paper_bgcolor=COLORS["card"],
        font=dict(family="Inter, sans-serif", color=COLORS["text"], size=12),
        margin=dict(l=40, r=20, t=46 if title else 16, b=36),
        height=height,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=11, color=COLORS["muted"]),
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor=COLORS["bg"], font=dict(color=COLORS["text"], family="Inter"),
            bordercolor=COLORS["amber"],
        ),
        xaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"],
                   tickfont=dict(color=COLORS["muted"], size=11),
                   title_font=dict(color=COLORS["muted"], size=11)),
        yaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"],
                   tickfont=dict(color=COLORS["muted"], size=11),
                   title_font=dict(color=COLORS["muted"], size=11)),
    )
    return fig


# ---- Fleet tab figures ----------------------------------------------------

def _fig_daily_km(trips: pd.DataFrame) -> go.Figure:
    daily = (trips.groupby(trips["date"].dt.date)["actual_km"]
             .sum().reset_index().rename(columns={"date": "day"}))
    daily["ma7"] = daily["actual_km"].rolling(7, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily["day"], y=daily["actual_km"], name="Daily km",
        marker=dict(color=COLORS["amber"], opacity=0.55),
        hovertemplate="<b>%{x|%a %d %b}</b><br>%{y:,.0f} km<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=daily["day"], y=daily["ma7"], name="7-day moving avg",
        mode="lines", line=dict(color=COLORS["cyan"], width=2.5),
        hovertemplate="MA7: %{y:,.0f} km<extra></extra>",
    ))
    return _apply_layout(fig, height=320, title="Daily kilometres driven")


def _fig_fuel_by_truck(trips: pd.DataFrame) -> go.Figure:
    by_truck = (trips.groupby(["truck_id", "model"])
                .agg(fuel=("fuel_l", "sum"), km=("actual_km", "sum"))
                .reset_index())
    by_truck["l100"] = by_truck["fuel"] / by_truck["km"] * 100
    by_truck = by_truck.sort_values("l100").head(15)

    model_color = {m: c for m, c in zip(TRUCK_MODELS, [
        COLORS["amber"], COLORS["cyan"], COLORS["emerald"],
        COLORS["violet"], COLORS["amber_soft"], COLORS["rose"],
    ])}
    fig = go.Figure(go.Bar(
        x=by_truck["l100"], y=by_truck["truck_id"], orientation="h",
        marker=dict(color=[model_color[m] for m in by_truck["model"]]),
        text=[f"{v:.1f}" for v in by_truck["l100"]],
        textposition="outside",
        textfont=dict(color=COLORS["muted"], size=11),
        hovertemplate="<b>%{y}</b><br>%{customdata}<br>%{x:.1f} L/100km<extra></extra>",
        customdata=by_truck["model"],
    ))
    fig.update_xaxes(title="L / 100km")
    return _apply_layout(fig, height=420, title="Most fuel-efficient trucks (top 15)")


def _fig_co2_by_model(trips: pd.DataFrame) -> go.Figure:
    monthly = trips.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").dt.to_timestamp()
    grouped = (monthly.groupby(["month", "model"])["co2_kg"]
               .sum().div(1000).reset_index())  # → tonnes

    fig = go.Figure()
    palette = [COLORS["amber"], COLORS["cyan"], COLORS["emerald"],
               COLORS["violet"], COLORS["amber_soft"], COLORS["rose"]]
    for model, color in zip(TRUCK_MODELS, palette):
        sub = grouped[grouped["model"] == model]
        fig.add_trace(go.Bar(
            x=sub["month"], y=sub["co2_kg"], name=model,
            marker=dict(color=color),
            hovertemplate="<b>%{x|%b %Y}</b><br>" + model + ": %{y:,.0f} t<extra></extra>",
        ))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title="CO₂, tonnes")
    return _apply_layout(fig, height=320, title="CO₂ emissions by truck model")


def _fig_efficiency_distribution(trips: pd.DataFrame) -> go.Figure:
    by_truck = trips.groupby(["truck_id", "model"]).agg(
        l100=("fuel_l_per_100km", "mean"),
        km=("actual_km", "sum"),
    ).reset_index()

    fig = go.Figure()
    palette = {m: c for m, c in zip(TRUCK_MODELS, [
        COLORS["amber"], COLORS["cyan"], COLORS["emerald"],
        COLORS["violet"], COLORS["amber_soft"], COLORS["rose"],
    ])}
    for model, color in palette.items():
        sub = by_truck[by_truck["model"] == model]
        fig.add_trace(go.Scatter(
            x=sub["km"], y=sub["l100"], mode="markers", name=model,
            marker=dict(color=color, size=12, line=dict(color=COLORS["bg"], width=1)),
            hovertemplate="<b>%{text}</b><br>" + model
                          + "<br>%{x:,.0f} km<br>%{y:.1f} L/100km<extra></extra>",
            text=sub["truck_id"],
        ))
    fig.update_xaxes(title="Distance driven (km)")
    fig.update_yaxes(title="L / 100km")
    return _apply_layout(fig, height=320, title="Truck efficiency vs distance")


# ---- Planning tab figures -------------------------------------------------

def _fig_empty_km_trend(trips: pd.DataFrame) -> go.Figure:
    weekly = trips.copy()
    weekly["week"] = weekly["date"].dt.to_period("W").dt.start_time
    grouped = (weekly.groupby(["week", "planner"])
               .agg(empty=("empty_km", "sum"), total=("actual_km", "sum"))
               .reset_index())
    grouped["empty_pct"] = grouped["empty"] / grouped["total"] * 100

    fig = go.Figure()
    palette = [COLORS["amber"], COLORS["cyan"], COLORS["emerald"], COLORS["violet"]]
    for planner, color in zip(PLANNERS, palette):
        sub = grouped[grouped["planner"] == planner]
        fig.add_trace(go.Scatter(
            x=sub["week"], y=sub["empty_pct"], name=planner,
            mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=6),
            hovertemplate="<b>" + planner + "</b><br>%{x|%d %b}<br>%{y:.1f}% empty<extra></extra>",
        ))
    fig.add_hline(y=15, line=dict(color=COLORS["rose"], dash="dash", width=1),
                  annotation_text="Target ≤15%",
                  annotation_position="top right",
                  annotation_font=dict(color=COLORS["rose"], size=10))
    fig.update_yaxes(title="Empty km %")
    return _apply_layout(fig, height=340, title="Empty kilometres % — weekly trend per planner")


def _fig_idle_per_planner(trips: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    palette = [COLORS["amber"], COLORS["cyan"], COLORS["emerald"], COLORS["violet"]]
    for planner, color in zip(PLANNERS, palette):
        sub = trips[trips["planner"] == planner]["idle_hours"]
        fig.add_trace(go.Box(
            y=sub, name=planner, marker=dict(color=color),
            line=dict(color=color), boxmean=True,
        ))
    fig.update_yaxes(title="Idle hours per trip")
    return _apply_layout(fig, height=320, title="Idle time distribution per planner")


def _fig_routes_per_planner(trips: pd.DataFrame) -> go.Figure:
    monthly = trips.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").dt.to_timestamp()
    grouped = monthly.groupby(["month", "planner"]).size().reset_index(name="routes")

    fig = go.Figure()
    palette = [COLORS["amber"], COLORS["cyan"], COLORS["emerald"], COLORS["violet"]]
    for planner, color in zip(PLANNERS, palette):
        sub = grouped[grouped["planner"] == planner]
        fig.add_trace(go.Scatter(
            x=sub["month"], y=sub["routes"], name=planner,
            mode="lines", stackgroup="one",
            line=dict(width=0.5, color=color),
            fillcolor=color,
            hovertemplate="<b>" + planner + "</b><br>%{x|%b %Y}<br>%{y} routes<extra></extra>",
        ))
    fig.update_yaxes(title="Routes")
    return _apply_layout(fig, height=320, title="Routes planned per month")


def _fig_on_time_per_planner(trips: pd.DataFrame) -> go.Figure:
    grouped = trips.groupby("planner").agg(
        on_time=("on_time", "sum"),
        total=("on_time", "size"),
    ).reset_index()
    grouped["late"] = grouped["total"] - grouped["on_time"]
    grouped["on_time_pct"] = grouped["on_time"] / grouped["total"] * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=grouped["planner"], x=grouped["on_time"], orientation="h",
        name="On time", marker=dict(color=COLORS["emerald"]),
        hovertemplate="On time: %{x:,}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=grouped["planner"], x=grouped["late"], orientation="h",
        name="Late", marker=dict(color=COLORS["rose"]),
        text=[f"{p:.0f}% on-time" for p in grouped["on_time_pct"]],
        textposition="outside",
        textfont=dict(color=COLORS["muted"], size=11),
        hovertemplate="Late: %{x:,}<extra></extra>",
    ))
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title="Trips")
    return _apply_layout(fig, height=320, title="On-time vs late trips per planner")


# ---- Forwarders tab figures ----------------------------------------------

def _fig_volume_per_forwarder(trips: pd.DataFrame) -> go.Figure:
    monthly = trips.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").dt.to_timestamp()
    grouped = (monthly.groupby(["month", "forwarder"])["tonnes"]
               .sum().reset_index())

    fig = go.Figure()
    palette = [COLORS["amber"], COLORS["cyan"], COLORS["emerald"],
               COLORS["violet"], COLORS["rose"]]
    for forwarder, color in zip(FORWARDERS, palette):
        sub = grouped[grouped["forwarder"] == forwarder]
        fig.add_trace(go.Bar(
            x=sub["month"], y=sub["tonnes"], name=forwarder,
            marker=dict(color=color),
            hovertemplate="<b>%{x|%b %Y}</b><br>" + forwarder + ": %{y:,.0f} t<extra></extra>",
        ))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title="Tonnes")
    return _apply_layout(fig, height=340, title="Volume per forwarder (incl. in-house)")


def _fig_cpk_comparison(trips: pd.DataFrame) -> go.Figure:
    grouped = (trips.groupby("forwarder")
               .agg(cost=("cost_eur", "sum"), km=("actual_km", "sum"))
               .reset_index())
    grouped["cpk"] = grouped["cost"] / grouped["km"]
    grouped = grouped.sort_values("cpk")

    colors = [COLORS["amber"] if f == "In-house fleet" else COLORS["cyan"]
              for f in grouped["forwarder"]]
    fig = go.Figure(go.Bar(
        x=grouped["cpk"], y=grouped["forwarder"], orientation="h",
        marker=dict(color=colors),
        text=[f"€ {v:.2f}" for v in grouped["cpk"]],
        textposition="outside",
        textfont=dict(color=COLORS["text"], size=11),
        hovertemplate="<b>%{y}</b><br>€ %{x:.2f} / km<extra></extra>",
    ))
    fig.update_xaxes(title="€ per km")
    return _apply_layout(fig, height=300, title="Cost per km — in-house vs forwarders")


def _fig_otp_per_forwarder(trips: pd.DataFrame) -> go.Figure:
    grouped = (trips.groupby("forwarder")
               .agg(otp=("on_time", "mean"), n=("on_time", "size"))
               .reset_index())
    grouped["otp"] = grouped["otp"] * 100
    grouped = grouped.sort_values("otp")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=grouped["otp"], y=grouped["forwarder"], mode="markers",
        marker=dict(size=18, color=COLORS["amber"],
                    line=dict(color=COLORS["bg"], width=2)),
        text=[f"{v:.1f}%" for v in grouped["otp"]],
        textposition="middle right",
        textfont=dict(color=COLORS["text"], size=11),
        hovertemplate="<b>%{y}</b><br>%{x:.1f}% on-time<br>%{customdata:,} trips<extra></extra>",
        customdata=grouped["n"],
        showlegend=False,
    ))
    # Horizontal "stem" lines.
    for _, row in grouped.iterrows():
        fig.add_shape(type="line",
                      x0=85, x1=row["otp"], y0=row["forwarder"], y1=row["forwarder"],
                      line=dict(color=COLORS["grid"], width=1))
    fig.update_xaxes(title="On-time %", range=[85, 100])
    return _apply_layout(fig, height=320, title="On-time delivery rate per forwarder")


def _fig_spend_share(trips: pd.DataFrame) -> go.Figure:
    grouped = trips.groupby("forwarder")["cost_eur"].sum().reset_index()
    palette = [COLORS["amber"], COLORS["cyan"], COLORS["emerald"],
               COLORS["violet"], COLORS["rose"]]
    fig = go.Figure(go.Pie(
        labels=grouped["forwarder"], values=grouped["cost_eur"],
        hole=0.55,
        marker=dict(colors=palette, line=dict(color=COLORS["bg"], width=2)),
        textinfo="percent",
        textfont=dict(color=COLORS["bg"], size=12, family="Inter"),
        hovertemplate="<b>%{label}</b><br>€ %{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(showlegend=True)
    return _apply_layout(fig, height=320, title="Spend share per forwarder")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def trucks_summary(period_days: Optional[int] = None) -> list:
    """Per-truck rollup used by the Fleet-tab table and the drill-down."""
    trips = _filter_by_period(_cached_dataset()["trips"], period_days)

    by_truck = trips.groupby(["truck_id", "model", "year"]).agg(
        trips_count=("date", "size"),
        total_km=("actual_km", "sum"),
        revenue=("cost_eur", "sum"),
        fuel_l=("fuel_l", "sum"),
        co2_kg=("co2_kg", "sum"),
        empty_km=("empty_km", "sum"),
        idle_h=("idle_hours", "sum"),
        on_time=("on_time", "sum"),
        avg_cpk=("cost_per_km_eur", "mean"),
        median_cpk=("cost_per_km_eur", "median"),
        max_cpk=("cost_per_km_eur", "max"),
        min_cpk=("cost_per_km_eur", "min"),
        l100=("fuel_l_per_100km", "mean"),
    ).reset_index()
    by_truck["on_time_pct"] = by_truck["on_time"] / by_truck["trips_count"] * 100
    by_truck["empty_pct"] = by_truck["empty_km"] / by_truck["total_km"] * 100
    by_truck = by_truck.sort_values("revenue", ascending=False)

    return [
        {
            "truck_id": r.truck_id,
            "model": r.model,
            "year": int(r.year),
            "trips": int(r.trips_count),
            "km": float(r.total_km),
            "revenue_eur": float(r.revenue),
            "fuel_l": float(r.fuel_l),
            "co2_t": float(r.co2_kg / 1000),
            "avg_cpk": float(r.avg_cpk),
            "median_cpk": float(r.median_cpk),
            "max_cpk": float(r.max_cpk),
            "min_cpk": float(r.min_cpk),
            "l100": float(r.l100),
            "on_time_pct": float(r.on_time_pct),
            "empty_pct": float(r.empty_pct),
            "idle_h": float(r.idle_h),
        }
        for r in by_truck.itertuples()
    ]


# ---- Per-truck drill-down -------------------------------------------------

def _fig_truck_revenue_weekly(truck_trips: pd.DataFrame) -> go.Figure:
    """Weekly revenue + €/km dual-axis. Weekly works for any period
    (30 d → 4-5 bars, 6 mo → ~25 bars) without single-point axis glitches.
    """
    weekly = truck_trips.copy()
    weekly["week"] = weekly["date"].dt.to_period("W").dt.start_time
    grouped = weekly.groupby("week").agg(
        revenue=("cost_eur", "sum"),
        km=("actual_km", "sum"),
    ).reset_index()
    grouped["cpk"] = grouped["revenue"] / grouped["km"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped["week"], y=grouped["revenue"], name="Revenue",
        marker=dict(color=COLORS["amber"]),
        hovertemplate="<b>w/c %{x|%d %b %Y}</b><br>€ %{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=grouped["week"], y=grouped["cpk"], name="€/km",
        yaxis="y2", mode="lines+markers",
        line=dict(color=COLORS["cyan"], width=2),
        marker=dict(size=5),
        hovertemplate="€/km: %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(
        yaxis=dict(title="Revenue €"),
        yaxis2=dict(title="€ / km", overlaying="y", side="right",
                    showgrid=False, tickfont=dict(color=COLORS["cyan"]),
                    title_font=dict(color=COLORS["cyan"])),
        xaxis=dict(tickformat="%d %b"),
        # Wider right gutter so the secondary "€ / km" axis label fits
        # without clipping inside the drawer.
        margin=dict(l=50, r=58, t=46, b=36),
    )
    return _apply_layout(fig, height=260, title="Weekly revenue & cost-per-km")


def _fig_truck_route_map(truck_trips: pd.DataFrame) -> go.Figure:
    """Schematic EU route map: lon/lat as cartesian axes, no basemap.

    Why not Scattergeo? Plotly's geo subplot needs the container to have
    measured width when it first paints; inside an animated drawer this
    races the transition and the map silently fails to draw. A plain
    cartesian Scatter with lon/lat as x/y ALWAYS renders, requires zero
    external services or vector data, and reads as a clean cockpit-style
    schematic when styled in the same dark palette."""
    pair_counts = (truck_trips
                   .groupby(["origin", "destination"])
                   .size().reset_index(name="trips")
                   .sort_values("trips", ascending=False))

    fig = go.Figure()
    max_trips = max(pair_counts["trips"].max(), 1)

    # Routes: amber lines, width + opacity scaled by trip frequency.
    for _, row in pair_counts.iterrows():
        o_lat, o_lon = EUROPEAN_HUBS[row["origin"]]
        d_lat, d_lon = EUROPEAN_HUBS[row["destination"]]
        weight = row["trips"] / max_trips
        fig.add_trace(go.Scatter(
            x=[o_lon, d_lon], y=[o_lat, d_lat],
            mode="lines",
            line=dict(width=1 + 2.5 * weight, color=COLORS["amber"]),
            opacity=0.35 + 0.55 * weight,
            hoverinfo="skip",
            showlegend=False,
        ))

    # Hub markers — sized by total visits (origin OR destination).
    visits = pd.concat([
        truck_trips["origin"].rename("city"),
        truck_trips["destination"].rename("city"),
    ]).value_counts().reset_index(name="visits")
    visits.columns = ["city", "visits"]
    visits["lat"] = visits["city"].map(lambda c: EUROPEAN_HUBS[c][0])
    visits["lon"] = visits["city"].map(lambda c: EUROPEAN_HUBS[c][1])
    max_visits = max(visits["visits"].max(), 1)

    fig.add_trace(go.Scatter(
        x=visits["lon"], y=visits["lat"], text=visits["city"],
        mode="markers+text",
        marker=dict(
            size=10 + (visits["visits"] / max_visits) * 20,
            color=COLORS["cyan"],
            line=dict(color=COLORS["bg"], width=2),
            opacity=0.95,
        ),
        textfont=dict(color=COLORS["text"], size=11, family="Inter"),
        textposition="top center",
        hovertemplate="<b>%{text}</b><br>%{customdata} visits<extra></extra>",
        customdata=visits["visits"],
        showlegend=False,
    ))

    fig.update_layout(
        plot_bgcolor=COLORS["bg"],
        paper_bgcolor=COLORS["card"],
        font=dict(family="Inter, sans-serif", color=COLORS["text"], size=12),
        margin=dict(l=20, r=20, t=20, b=20),
        height=400,
        hoverlabel=dict(bgcolor=COLORS["bg"], bordercolor=COLORS["amber"],
                        font=dict(color=COLORS["text"])),
        xaxis=dict(
            visible=False,
            range=[-9, 26],
            constrain="domain",
        ),
        yaxis=dict(
            visible=False,
            range=[34, 57],     # padded south so Madrid label has headroom
            scaleanchor="x",
            scaleratio=1.3,     # ~Mercator-ish aspect for EU
            constrain="domain",
        ),
    )
    return fig


def truck_detail(truck_id: str, period_days: Optional[int] = None) -> Dict:
    trips_all = _cached_dataset()["trips"]
    truck_trips = _filter_by_period(trips_all, period_days)
    truck_trips = truck_trips[truck_trips["truck_id"] == truck_id]

    if truck_trips.empty:
        return {"error": "No trips for this truck in the selected period."}

    truck_meta = (_cached_dataset()["trucks"]
                  .query("truck_id == @truck_id").iloc[0])

    total_km = float(truck_trips["actual_km"].sum())
    total_rev = float(truck_trips["cost_eur"].sum())

    # Top 5 routes by trip count
    top_routes = (truck_trips
                  .groupby(["origin", "destination"])
                  .agg(trips=("date", "size"),
                       avg_cpk=("cost_per_km_eur", "mean"),
                       total_km=("actual_km", "sum"))
                  .reset_index()
                  .sort_values("trips", ascending=False)
                  .head(5))
    top_routes_payload = [
        {
            "from": r.origin, "to": r.destination,
            "trips": int(r.trips), "avg_cpk": float(r.avg_cpk),
            "km": float(r.total_km),
        }
        for r in top_routes.itertuples()
    ]

    stats = {
        "truck_id": truck_id,
        "model": str(truck_meta["model"]),
        "year": int(truck_meta["year"]),
        "trips": int(len(truck_trips)),
        "total_km": total_km,
        "loaded_km": float(truck_trips["loaded_km"].sum()),
        "empty_km": float(truck_trips["empty_km"].sum()),
        "empty_pct": float(truck_trips["empty_km"].sum() / total_km * 100),
        "fuel_l": float(truck_trips["fuel_l"].sum()),
        "co2_t": float(truck_trips["co2_kg"].sum() / 1000),
        "l100": float(truck_trips["fuel_l_per_100km"].mean()),
        "revenue_eur": total_rev,
        "avg_cpk": float(truck_trips["cost_per_km_eur"].mean()),
        "median_cpk": float(truck_trips["cost_per_km_eur"].median()),
        "max_cpk": float(truck_trips["cost_per_km_eur"].max()),
        "min_cpk": float(truck_trips["cost_per_km_eur"].min()),
        "on_time_pct": float(truck_trips["on_time"].mean() * 100),
        "idle_h_total": float(truck_trips["idle_hours"].sum()),
        "tonnes_hauled": float(truck_trips["tonnes"].sum()),
    }

    figures = {
        "truck_revenue": pio.to_json(_fig_truck_revenue_weekly(truck_trips)),
        "truck_map": pio.to_json(_fig_truck_route_map(truck_trips)),
    }

    return {"stats": stats, "top_routes": top_routes_payload, "figures": figures}


@lru_cache(maxsize=8)
def build_demo(period_days: Optional[int] = None) -> Dict[str, object]:
    """Return KPIs + figure-JSON dict for the cockpit template.

    Cached per period_days. The first call generates mock data once and
    re-uses it across periods (only re-aggregates).
    """
    trips_all = _cached_dataset()["trips"]
    trips = _filter_by_period(trips_all, period_days)

    kpis = _compute_kpis(trips)

    figures = {
        # Fleet
        "fleet_daily_km": _fig_daily_km(trips),
        "fleet_fuel_by_truck": _fig_fuel_by_truck(trips),
        "fleet_co2_by_model": _fig_co2_by_model(trips),
        "fleet_efficiency": _fig_efficiency_distribution(trips),
        # Planning
        "plan_empty_trend": _fig_empty_km_trend(trips),
        "plan_idle_box": _fig_idle_per_planner(trips),
        "plan_routes_area": _fig_routes_per_planner(trips),
        "plan_on_time": _fig_on_time_per_planner(trips),
        # Forwarders
        "fwd_volume": _fig_volume_per_forwarder(trips),
        "fwd_cpk": _fig_cpk_comparison(trips),
        "fwd_otp": _fig_otp_per_forwarder(trips),
        "fwd_spend": _fig_spend_share(trips),
    }
    figures_json = {k: pio.to_json(v) for k, v in figures.items()}

    period_label = (trips["date"].min().strftime("%d %b %Y")
                    + " — " + trips["date"].max().strftime("%d %b %Y"))
    meta = {
        "period": period_label,
        "period_days": period_days,
        "fleet_size": int(trips["truck_id"].nunique()),
        "total_trips": int(len(trips)),
        "planners": list(PLANNERS),
        "forwarders": list(FORWARDERS),
    }

    return {
        "kpis": kpis,
        "figures": figures_json,
        "meta": meta,
        "trucks": trucks_summary(period_days),
    }
