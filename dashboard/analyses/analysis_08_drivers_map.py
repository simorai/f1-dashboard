"""Analysis 08 - Geographic distribution of drivers.

Demonstrates: joining drivers with circuits (for coordinates where useful),
aggregating counts by nationality and rendering them on a world map with
Plotly, plus a bar chart and a table.
"""

from __future__ import annotations

import streamlit as st

from dashboard import charts, components, data_loader as dl, preprocessor


# ISO-3 codes are required by Plotly's choropleth / scatter_geo. Mapping the
# handful of nationalities present in the dataset keeps the map correct.
# A dict here is the simplest data structure for a fixed lookup.
NATIONALITY_TO_ISO3: dict[str, str] = {
    "British": "GBR", "German": "DEU", "Brazilian": "BRA", "French": "FRA",
    "Italian": "ITA", "Spanish": "ESP", "Finnish": "FIN", "Australian": "AUS",
    "Austrian": "AUT", "Dutch": "NLD", "American": "USA", "Canadian": "CAN",
    "Swiss": "CHE", "Belgian": "BEL", "Swedish": "SWE", "Japanese": "JPN",
    "Mexican": "MEX", "Argentine": "ARG", "New Zealander": "NZL",
    "South African": "ZAF", "Monégasque": "MCO", "Danish": "DNK",
    "Polish": "POL", "Russian": "RUS", "Colombian": "COL", "Venezuelan": "VEN",
    "Portuguese": "PRT", "Irish": "IRL", "Hungarian": "HUN", "Czech": "CZE",
    "Chilean": "CHL", "Thai": "THA", "Malaysian": "MYS", "Indonesian": "IDN",
    "Chinese": "CHN", "Indian": "IND", "Turkish": "TUR", "Uruguayan": "URY",
    "Rhodesian": "ZWE", "East German": "DEU", "Liechtensteiner": "LIE",
}


def render() -> None:
    """Draw the "Drivers on a Map" page."""
    components.page_header(
        "Drivers on a Map",
        "Where do Formula 1 drivers come from?",
        "🌍",
    )

    drivers = preprocessor.add_full_name(dl.load_drivers())

    # Count drivers per nationality, then translate to ISO-3 for the map.
    counts = (
        drivers["nationality"].value_counts()
        .rename_axis("Nationality").reset_index(name="Drivers")
    )
    counts["ISO3"] = counts["Nationality"].map(NATIONALITY_TO_ISO3)

    # Keep only rows we can place on the map (unmapped nationalities dropped).
    mapped = counts.dropna(subset=["ISO3"])

    components.kpi_row(
        [
            ("Total drivers", len(drivers)),
            ("Nationalities", drivers["nationality"].nunique()),
            ("Top nationality", counts.iloc[0]["Nationality"]),
        ]
    )

    import plotly.express as px

    fig = px.choropleth(
        mapped, locations="ISO3", color="Drivers",
        hover_name="Nationality", color_continuous_scale="Reds",
        locationmode="ISO-3", title="Drivers per nationality (world map)",
    )
    fig.update_geos(showcountries=True, showcoastlines=True,
                    showframe=False, projection_type="natural earth")
    charts.show(fig)

    left, right = st.columns((3, 2))
    with left:
        bar = charts.bar_chart(
            counts.head(15), x="Drivers", y="Nationality", orientation="h",
            title="Top 15 driver nationalities",
        )
        charts.show(bar)
    with right:
        components.data_table(counts, title="Drivers per nationality")
