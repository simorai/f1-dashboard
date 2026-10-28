"""Application entry point for the Formula 1 Streamlit dashboard.

This file is intentionally *thin*: it configures the page, renders the sidebar
navigation from the analysis registry, and dispatches to the selected page. All
real logic lives in the ``dashboard`` package so this file stays easy to read
(and is the opposite of a "god class").

Run with:  streamlit run main.py
"""

from __future__ import annotations

import streamlit as st

from dashboard import charts, components, config, preprocessor
from dashboard.analyses import ANALYSES, get_analysis


def configure_page() -> None:
    """Set page config once, before any other Streamlit output."""
    # ``set_page_config`` must be the first Streamlit call in the script.
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon=config.APP_ICON,
        layout=config.APP_LAYOUT,
    )


def render_home() -> None:
    """Home page: hero media, intro, dataset overview (EDA) and quick links."""
    # Multimedia banner inside a container.
    with st.container():
        components.media_banner(
            config.HERO_GIF_URL,
            caption="Formula 1 Analytics — an interactive data story 🏎️",
        )

    components.page_header(
        "Formula 1 Analytics",
        "Explore decades of F1 data across eight interactive analyses.",
        "🏎️",
    )

    # Short intro laid out in two columns.
    intro_left, intro_right = st.columns((3, 2))
    with intro_left:
        st.markdown(
            """
            ### What is this?
            This dashboard turns the classic **Ergast Formula 1 dataset**
            (1950–2024) into an interactive exploration tool. Use the sidebar
            to jump between analyses such as *race wins*, *pit stops*, *reliability* and *lap times*.
            """
        )
    with intro_right:
        # The official F1 logo.
        st.image(config.F1_LOGO_URL, width=160)

    # --- EDA: dataset overview table --------------------------------------
    st.subheader("📊 Dataset overview (EDA)")
    components.data_table(
        preprocessor.dataset_overview(),
        title="Datasets used by this dashboard",
    )

    # A tiny teaser chart so the home page is not only tables.
    fact = preprocessor.build_results_fact()
    wins_by_decade = (
        fact[fact["position"] == 1]
        .assign(decade=lambda d: (d["year"] // 10) * 10)
        .groupby("decade").size().reset_index(name="Wins")
    )
    charts.show(
        charts.bar_chart(
            wins_by_decade, x="decade", y="Wins",
            title="Race wins per decade",
        )
    )


def render_sidebar() -> str:
    """Draw sidebar navigation and return the selected slug.

    Navigation is driven by the ``ANALYSES`` registry, so adding a page never
    requires editing this function.
    """
    with st.sidebar:
        st.image(config.F1_LOGO_URL, width=120)
        st.markdown("## Navigation")

        # Build a label->slug mapping; "🏠 Home" is a special first entry.
        options: dict[str, str] = {"🏠 Home": "home"}
        for analysis in ANALYSES:
            options[f"{analysis.icon} {analysis.title}"] = analysis.slug

        # ``radio`` always-visible way to navigate.
        choice = st.radio("Go to", list(options.keys()),
                          label_visibility="collapsed")

        st.divider()
        st.caption(
            "Built with Streamlit · pandas · Plotly\n\n"
            "Data source: Ergast F1 dataset (1950–2024).\n\n" \
            "Simao Morais, 2026. Licensed under MIT.\n\n" \
            "Source code: [GitHub](https://github.com/simao-morais/f1-dashboard)"
        )
    return options[choice]


def main() -> None:
    """Wire configuration, navigation and page rendering together."""
    configure_page()
    selected = render_sidebar()

    # Dispatch: Home is special; everything else goes through the registry.
    if selected == "home":
        render_home()
    else:
        analysis = get_analysis(selected)
        analysis.render()


# Standard Python guard so ``import main`` (e.g. in tests) does not run the app.
if __name__ == "__main__":
    main()
