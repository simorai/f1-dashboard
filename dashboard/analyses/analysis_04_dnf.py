"""Analysis 04 - Reliability: Did Not Finish (DNF) reasons.

Demonstrates: merging results with the status lookup, separating mechanical
from incident DNFs, a bar chart of DNF causes, a per-decade line trend and a
pie of DNF categories.
"""

from __future__ import annotations

import streamlit as st

from dashboard import charts, components, data_loader as dl, preprocessor


def render() -> None:
    """Draw the "Reliability / DNFs" page."""
    components.page_header(
        "Reliability / DNFs",
        "Why do cars fail to finish?",
        "🛑",
    )

    results = preprocessor.clean_results(dl.load_results())
    status = dl.load_status()
    races = dl.load_races()

    # Attach the human status text and the race year.
    df = (
        results.merge(status, on="statusId", how="left")
        .merge(races[["raceId", "year"]], on="raceId", how="left")
    )

    # A DNF is anything that did not "finish" in a classified running state.
    # Ergast uses status == 'Finished' or '+N Lap(s)' for cars still running.
    running = df["status"].str.startswith(("Finished", "+"))
    dnf = df[~running & (df["status"] != "Disqualified")].copy()
    # Treat a disqualification as its own bucket too.
    dnf.loc[df["status"] == "Disqualified", "status"] = "Disqualified"

    # --- top DNF causes ----------------------------------------------------
    cause_counts = (
        dnf["status"].value_counts().head(12)
        .rename_axis("Reason").reset_index(name="Count")
    )

    # --- DNF rate per season ----------------------------------------------
    per_season = (
        df.assign(dnf=~running)
        .groupby("year")["dnf"].mean()
        .mul(100).reset_index(name="DNF %")
    )

    with st.container(border=True):
        win = st.slider(
            "Season range",
            int(races["year"].min()), int(races["year"].max()),
            (1990, int(races["year"].max())),
        )
    per_season = per_season[
        (per_season["year"] >= win[0]) & (per_season["year"] <= win[1])
    ]
    cause_counts = (
        dnf[(dnf["year"] >= win[0]) & (dnf["year"] <= win[1])]["status"]
        .value_counts().head(12)
        .rename_axis("Reason").reset_index(name="Count")
    )

    components.kpi_row(
        [
            ("Total retirements", len(dnf)),
            ("Distinct causes", dnf["status"].nunique()),
            ("Latest-season DNF %", f"{per_season['DNF %'].iloc[-1]:.1f}%"),
        ]
    )

    left, right = st.columns(2)
    with left:
        bar = charts.bar_chart(
            cause_counts, x="Count", y="Reason", orientation="h",
            title="Most common retirement causes",
        )
        charts.show(bar)
    with right:
        line = charts.line_chart(
            per_season, x="year", y="DNF %",
            title="DNF rate (%) over the seasons",
        )
        charts.show(line)

    # Categorise causes into Mechanical vs Incident for a pie.
    st.subheader("Mechanical failures vs incidents")
    mechanical_keywords = (
        "Engine", "Gearbox", "Transmission", "Clutch", "Hydraulics",
        "Electrical", "Brakes", "Suspension", "Oil", "Water", "Fuel",
        "Overheating", "Turbo", "Exhaust", "Radiator", "ERs",
    )

    def categorise(reason: str) -> str:
        """Return a category for a DNF reason."""
        return "Mechanical" if any(k.lower() in reason.lower()
                                   for k in mechanical_keywords) else "Incident"

    dnf["Category"] = dnf["status"].apply(categorise)
    cat = dnf["Category"].value_counts().rename_axis("Category") \
        .reset_index(name="Count")
    charts.show(charts.pie_chart(cat, names="Category", values="Count",
                                 title="DNF split by category"))

    components.data_table(cause_counts, title="Retirement reasons")
