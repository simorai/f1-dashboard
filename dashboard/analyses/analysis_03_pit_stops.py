"""Analysis 03 - Pit stop performance by team.

Demonstrates: loading the (large) pit_stops file *only when this page is
used*, deriving numeric seconds from milliseconds, per-team distribution with
a box plot, an average-ranking bar chart and a results merge.
"""

from __future__ import annotations

import streamlit as st

from dashboard import charts, components, data_loader as dl, preprocessor


def render() -> None:
    """Draw the "Pit Stop Performance" page."""
    components.page_header(
        "Pit Stop Performance",
        "Who has the fastest pit crews?",
        "🔧",
    )

    # Only load the files this analysis needs
    # pit_stops (durations) + constructors (names) + results (team per race).
    pit = dl.load_pit_stops()
    results = dl.load_results()
    constructors = dl.load_constructors()
    races = dl.load_races()

    # Robustly derive numeric seconds from the (always numeric) milliseconds
    # column. The raw ``duration`` text mixes "26.898" and "1:44.833" formats.
    pit = preprocessor.parse_pit_duration(pit)

    with st.container(border=True):
        year_col, min_stops_col = st.columns(2)
        years = sorted(races["year"].unique())
        with year_col:
            year = st.selectbox("Season", years, index=len(years) - 1)
        with min_stops_col:
            min_stops = st.slider("Minimum stops per team", 1, 50, 10)

    # Map each pit stop to its race year, then filter to the chosen season.
    pit_year = pit.merge(races[["raceId", "year"]], on="raceId", how="left")
    pit_season = pit_year[pit_year["year"] == year]

    # Bring in the constructor for each stop (driver+race identifies the car).
    pit_season = pit_season.merge(
        results[["raceId", "driverId", "constructorId"]],
        on=["raceId", "driverId"], how="left",
    ).merge(
        constructors[["constructorId", "name"]],
        on="constructorId", how="left",
    ).rename(columns={"name": "Constructor"})

    if pit_season.empty:
        st.warning("No pit stop data for this season.")
        return

    # Aggregate: count stops and mean/median duration per team.
    agg = (
        pit_season.groupby("Constructor")["duration_seconds"]
        .agg(Stops="count", Avg="mean", Median="median")
        .reset_index()
    )
    agg = agg[agg["Stops"] >= min_stops].sort_values("Avg")
    # Round for cleaner display.
    agg[["Avg", "Median"]] = agg[["Avg", "Median"]].round(3)

    # Guard: if the minimum-stops filter removed everything, stop early.
    if agg.empty:
        st.info("No teams match the current filters. Lower the minimum stops.")
        return

    # KPI cards: fastest team + overall session average (Streamlit metrics).
    components.kpi_row(
        [
            ("Season", year),
            ("Fastest average team", agg.iloc[0]["Constructor"]),
            ("Best avg stop (s)", agg.iloc[0]["Avg"]),
            ("Teams analysed", len(agg)),
        ]
    )

    left, right = st.columns((3, 2))
    with left:
        # Distribution of stops per team shows consistency, not just the mean.
        box = charts.box_chart(
            pit_season[pit_season["Constructor"].isin(agg["Constructor"])],
            x="Constructor", y="duration_seconds",
            title=f"Pit stop duration distribution — {year}",
        )
        # Cap the y-axis so a few slow outlier stops don't squash the box.
        box.update_yaxes(
            range=[0, pit_season["duration_seconds"].quantile(0.98)]
        )
        charts.show(box)
    with right:
        bar = charts.bar_chart(
            agg, x="Avg", y="Constructor", orientation="h",
            title="Average pit stop duration (s)",
        )
        charts.show(bar)

    components.data_table(agg, title="Pit stop summary by team")
