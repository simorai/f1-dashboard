"""Analysis 07 - Lap-by-lap pace for a selected race.

Demonstrates: loading the very large ``lap_times.csv`` only here, letting the
user drill from season -> race -> drivers, and drawing a multi-series line
chart of lap times plus a box plot of per-driver pace.
"""

from __future__ import annotations

import streamlit as st

from dashboard import charts, components, data_loader as dl, preprocessor


def render() -> None:
    """Draw the "Lap Time Analysis" page."""
    components.page_header(
        "Lap Time Analysis",
        "Lap-by-lap pace for a single Grand Prix",
        "🔄",
    )

    # Needed files, loaded lazily here only.
    races = dl.load_races()
    drivers = preprocessor.add_full_name(dl.load_drivers())

    # Two cascading selectors: choose season, then a race from that season.
    # Present races chronologically (by round) so the list reads like a
    # calendar, not alphabetically.
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            year = st.selectbox(
                "Season",
                sorted(races["year"].unique(), reverse=True),
            )
        season_races = (
            races[races["year"] == year].sort_values("round")
        )
        with col2:
            race_name = st.selectbox(
                "Race (round order)", season_races["name"].tolist()
            )

    # Resolve the chosen race to its id (a season hosts each name once).
    race_row = season_races[season_races["name"] == race_name].iloc[0]
    race_id = int(race_row["raceId"])

    # Load lap times, then filter to just this race as early as possible to
    # avoid carrying the 500k+ row frame around.
    laps = dl.load_lap_times()
    laps = laps[laps["raceId"] == race_id]

    if laps.empty:
        st.warning("No lap time data available for this race.")
        return

    # Let the user pick a few drivers to compare (keep the chart readable).
    laps = laps.merge(drivers[["driverId", "full_name"]],
                      on="driverId", how="left")
    all_drivers = sorted(laps["full_name"].dropna().unique())
    chosen = st.multiselect(
        "Compare drivers", all_drivers, default=all_drivers[:5]
    )
    if not chosen:
        st.info("Select at least one driver to plot lap times.")
        return

    plot_df = laps[laps["full_name"].isin(chosen)]

    # Convert ms -> seconds for a readable axis.
    plot_df = plot_df.assign(lap_seconds=plot_df["milliseconds"] / 1000)

    components.kpi_row(
        [
            ("Race", race_name),
            ("Season", year),
            ("Laps recorded", int(laps["lap"].max())),
            ("Drivers compared", len(chosen)),
        ]
    )

    line = charts.line_chart(
        plot_df, x="lap", y="lap_seconds", color="full_name",
        title=f"Lap times — {race_name} {year}",
    )
    line.update_yaxes(title="Lap time (s)")
    line.update_xaxes(title="Lap")
    charts.show(line)

    # Box plot summarising each driver's pace distribution.
    st.subheader("Pace distribution")
    box = charts.box_chart(
        plot_df, x="full_name", y="lap_seconds",
        title="Lap time spread per driver",
    )
    charts.show(box)

    # Table: quick per-driver stats (best lap, median, laps completed).
    summary = (
        plot_df.groupby("full_name")["lap_seconds"]
        .agg(Best="min", Median="median", Laps="count")
        .round(3).reset_index()
    )
    components.data_table(summary, title="Per-driver lap summary")
