"""Analysis 06 - Grid to finish position change.

Demonstrates: computing a derived metric (positions gained/lost), grouping to
find the best overtakers, and a diverging bar chart.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard import charts, components, data_loader as dl, preprocessor


def render() -> None:
    """Draw the "Grid to Finish" page."""
    components.page_header(
        "Grid to Finish",
        "Who gains the most positions on race day?",
        "🚦",
    )

    results = preprocessor.clean_results(dl.load_results())
    drivers = preprocessor.add_full_name(dl.load_drivers())
    races = dl.load_races()

    years = sorted(races["year"].unique())
    with st.container(border=True):
        year = st.selectbox("Season", years, index=len(years) - 1)

    races_year = races[races["year"] == year][["raceId"]]
    df = (
        results.merge(races_year, on="raceId", how="inner")
        .dropna(subset=["grid", "position"])      # ignore pit-lane/DNF rows
        # Only count rows where the driver actually started (grid > 0).
        .query("grid > 0")
        .merge(drivers[["driverId", "full_name"]], on="driverId", how="left")
    )

    # Positions gained = grid - finish (positive => moved forward).
    df["gained"] = df["grid"] - df["position"]

    if df.empty:
        st.warning("No grid data for this season.")
        return

    # Per-driver totals.
    per_driver = (
        df.groupby("full_name")["gained"]
        .agg(Total="sum", Races="count", Avg="mean")
        .reset_index()
        .sort_values("Total", ascending=False)
    )
    per_driver[["Avg"]] = per_driver[["Avg"]].round(2)

    best = per_driver.head(3)
    worst = per_driver.tail(3)

    components.kpi_row(
        [
            ("Season", year),
            ("Best overtaker", per_driver.iloc[0]["full_name"]),
            ("Net positions gained", int(per_driver.iloc[0]["Total"])),
        ]
    )

    # Highlight the extremes: top 8 gainers and bottom 8 losers.
    plot_df = pd.concat([per_driver.head(8), per_driver.tail(8)])

    bar = charts.bar_chart(
        plot_df, x="Total", y="full_name", orientation="h",
        title=f"Net positions gained — {year}",
    )
    # Colour bars by sign: green gains, red losses (diverging bar chart).
    bar.update_traces(
        marker_color=[
            "#2CA02C" if v >= 0 else "#E10600" for v in plot_df["Total"]
        ]
    )
    charts.show(bar)

    left, right = st.columns(2)
    with left:
        components.data_table(best, title="Top gainers")
    with right:
        components.data_table(worst, title="Biggest losers")

    components.data_table(per_driver, title="Full standings by net gain")
