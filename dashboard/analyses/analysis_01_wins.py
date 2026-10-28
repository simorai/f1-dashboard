"""Analysis 01 - Most race wins by constructor and by driver.

Demonstrates: aggregation with ``value_counts``/``groupby``, top-N filtering,
a bar plot, a pie (share) plot and a supporting table.
"""

from __future__ import annotations

import streamlit as st

from dashboard import charts, components, preprocessor


def render() -> None:
    """Draw the "Most Race Wins" page."""
    components.page_header(
        "Most Race Wins", "All-time race victories in Formula 1", "🏆"
    )

    fact = preprocessor.build_results_fact()
    wins = fact[fact["position"] == 1]

    with st.container(border=True):
        top_n = st.slider("Show top N", min_value=5, max_value=20, value=10)

    # --- by constructor ----------------------------------------------------
    team_wins = (
        wins["constructor_name"].value_counts()
        .head(top_n)
        .rename_axis("Constructor")
        .reset_index(name="Wins")
    )

    # --- by driver ---------------------------------------------------------
    driver_wins = (
        wins["full_name"].value_counts()
        .head(top_n)
        .rename_axis("Driver")
        .reset_index(name="Wins")
    )

    left, right = st.columns(2)
    with left:
        fig = charts.bar_chart(
            team_wins, x="Wins", y="Constructor", orientation="h",
            title=f"Top {top_n} constructors by wins",
        )
        charts.show(fig)
    with right:
        fig = charts.bar_chart(
            driver_wins, x="Wins", y="Driver", orientation="h",
            title=f"Top {top_n} drivers by wins",
        )
        charts.show(fig)

    # --- share of all wins as a piechart -------------------------------------
    st.subheader("Share of race wins (top teams)")
    pie_fig = charts.pie_chart(
        team_wins, names="Constructor", values="Wins",
        title="Proportion of wins among top constructors",
    )
    charts.show(pie_fig)

    # --- data table --------------------------------------------------------
    components.data_table(team_wins, title="Constructor win counts")
