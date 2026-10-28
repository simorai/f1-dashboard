"""Analysis 02 - Points evolution of top teams per season.

Demonstrates: groupby aggregation across two keys, filtering to the best
teams, a multi-series line chart and a stacked area chart.
"""

from __future__ import annotations

import streamlit as st

from dashboard import charts, components, preprocessor


def render() -> None:
    """Draw the "Points Evolution" page."""
    components.page_header(
        "Points Evolution",
        "Season-by-season points of the most successful teams",
        "📈",
    )

    # Merge results with races/drivers/constructors once (shared fact table).
    fact = preprocessor.build_results_fact()

    with st.container(border=True):
        n_teams = st.slider("Number of top teams", 3, 10, 5)

    # Rank teams by total points ever; keep only the top-N.
    top_teams = (
        fact.groupby("constructor_name")["points"].sum()
        .nlargest(n_teams).index
    )
    # Sum points per season for those teams -> one row per (year, team).
    team_year = (
        fact[fact["constructor_name"].isin(top_teams)]
        .groupby(["year", "constructor_name"], as_index=False)
        .agg({"points": "sum"})
    )

    # Line chart: one line per team (``color`` splits the series).
    line_fig = charts.line_chart(
        team_year, x="year", y="points", color="constructor_name",
        title="Points per season (top teams)",
    )
    charts.show(line_fig)

    # Additional view: cumulative-style stacked area of the same data.
    st.subheader("Stacked view")
    area_fig = charts.area_chart(
        team_year, x="year", y="points", color="constructor_name",
        title="Stacked points distribution by season",
    )
    charts.show(area_fig)

    # Supporting table: pivot so seasons are rows and teams are columns.
    pivot = (
        team_year.pivot(index="year", columns="constructor_name",
                        values="points")
        .fillna(0).astype(int)
    )
    components.data_table(pivot, title="Points pivot (season × team)")
