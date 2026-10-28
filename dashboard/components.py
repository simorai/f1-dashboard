"""Reusable Streamlit UI building blocks.

Single Responsibility: presentation helpers that many pages share. Each
analysis calls these instead of re-implementing the same column/KPI/header
markup, which keeps the analysis modules tiny and consistent (DRY).

``st.container``/``st.columns`` come from the Streamlit layout API requested
by the brief (https://docs.streamlit.io/develop/api-reference/layout).
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from dashboard import config


def page_header(title: str, subtitle: str = "", icon: str = "") -> None:
    """Render a consistent page title block with an optional subtitle."""
    heading = f"{icon} {title}".strip()
    st.title(heading)
    if subtitle:
        st.caption(subtitle)
    st.divider()


def kpi_row(items: list[tuple[str, object]]) -> None:
    """Render a row of KPI metric cards.

    Parameters
    ----------
    items:
        List of ``(label, value)`` pairs. Using ``st.metric`` inside evenly
        sized columns gives the "dashboard card" look with zero custom CSS.
    """
    if not items:
        return
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        with col:
            st.metric(label=label, value=str(value))


def data_table(
    frame: pd.DataFrame,
    title: str = "",
    height: int | None = None,
    hide_index: bool = True,
) -> None:
    """Render a DataFrame with a small heading, using ``st.dataframe``.

    The brief requires data to be shown with ``table``/``dataframe`` or
    similar - this central helper enforces that consistently.
    """
    if title:
        st.markdown(f"**{title}**")
    kwargs: dict = {"width": "stretch", "hide_index": hide_index}
    if isinstance(height, int) and height > 0:
        kwargs["height"] = height
    st.dataframe(frame, **kwargs)


def two_column_layout() -> list:
    """Return a ``(left, right)`` pair of columns in a 3:2 ratio.

    A tiny convenience wrapper so pages don't hard-code the ratio everywhere.
    """
    return st.columns((3, 2))


def chart_and_table(chart_renderer, table_frame: pd.DataFrame,
                    table_title: str = "Data") -> None:
    """Render a chart on the left and its underlying data on the right.

    Encapsulates the most common page pattern in this dashboard (plot + table),
    so each analysis just passes a render function and a DataFrame.
    """
    left, right = two_column_layout()
    with left:
        chart_renderer()
    with right:
        data_table(table_frame, title=table_title, height=320)


def media_banner(image_url: str, caption: str = "") -> None:
    """Show a full-width image/GIF with an optional caption (multimedia)."""
    st.image(image_url, width="stretch")
    if caption:
        st.caption(caption)
