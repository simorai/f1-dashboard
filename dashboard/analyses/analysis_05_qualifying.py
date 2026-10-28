"""Analysis 05 - Qualifying vs Race outcome.

Demonstrates: loading ``qualifying.csv`` only here, merging qualifying and
results on (raceId, driverId), a scatter with a trendline and a correlation
metric.
"""

from __future__ import annotations

import streamlit as st

from dashboard import charts, components, data_loader as dl, preprocessor


def render() -> None:
    """Draw the "Qualifying vs Race" page."""
    components.page_header(
        "Qualifying vs Race",
        "Does qualifying pace predict race results?",
        "⏱️",
    )

    # Qualifying is only needed by this page -> loaded only here.
    qualifying = dl.load_qualifying()
    results = preprocessor.clean_results(dl.load_results())
    races = dl.load_races()
    drivers = preprocessor.add_full_name(dl.load_drivers())

    years = sorted(races["year"].unique())
    with st.container(border=True):
        year = st.selectbox("Season", years, index=len(years) - 1)

    # Restrict both frames to the chosen season using races.year.
    races_year = races[races["year"] == year][["raceId"]]
    qual = qualifying.merge(races_year, on="raceId", how="inner")
    res = results.merge(races_year, on="raceId", how="inner")

    # Merge qualifying position with finishing position per driver/race.
    merged = (
        qual[["raceId", "driverId", "position"]]
        .rename(columns={"position": "grid_qual"})
        .merge(
            res[["raceId", "driverId", "position", "points", "is_dnf"]]
            .rename(columns={"position": "finish"}),
            on=["raceId", "driverId"], how="inner",
        )
        # Drop non-finishers: they have no meaningful finishing position.
        .dropna(subset=["grid_qual", "finish"])
        .merge(drivers[["driverId", "full_name"]], on="driverId", how="left")
    )

    if merged.empty:
        st.warning("No qualifying/finish data for this season.")
        return

    # Correlation between qualifying and finishing position (-1..1).
    corr = merged["grid_qual"].corr(merged["finish"])

    components.kpi_row(
        [
            ("Season", year),
            ("Driver-race samples", len(merged)),
            ("Quali↔Finish correlation", f"{corr:.2f}"),
        ]
    )

    left, right = st.columns((3, 2))
    with left:
        scatter = charts.scatter_chart(
            merged, x="grid_qual", y="finish", color="points",
            hover_name="full_name",
            title=f"Qualifying position vs finishing position — {year}",
        )
        # Invert axes so P1 is top/left (intuitive "better is up/left").
        scatter.update_xaxes(autorange="reversed", title="Qualifying position")
        scatter.update_yaxes(autorange="reversed", title="Finishing position")
        charts.show(scatter)
    with right:
        # Average points scored by qualifying slot (binned into rows of 5).
        merged["quali_bin"] = (
            ((merged["grid_qual"] - 1) // 5 * 5 + 1)
            .astype(int).astype(str) + "–"
            + ((merged["grid_qual"] - 1) // 5 * 5 + 5)
            .astype(int).astype(str)
        )
        by_bin = (
            merged.groupby("quali_bin", as_index=False)
            .agg({"points": "mean"})
        )
        bar = charts.bar_chart(
            by_bin, x="quali_bin", y="points",
            title="Avg points by qualifying group",
        )
        charts.show(bar)

    components.data_table(
        merged.sort_values("finish")[
            ["full_name", "grid_qual", "finish", "points"]
        ].head(30),
        title="Sample rows (top-30 finishers)",
    )
