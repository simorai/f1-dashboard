"""Reusable Plotly chart builders.

Single Responsibility: translate tidy DataFrames into Plotly figures. Chart
*specs* live here exactly once; analyses supply data and pick a builder (DRY).
Plotly is used for its interactivity (hover, zoom, legend toggling) - one of
the tools explicitly allowed by the brief.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard import config


def _apply_theme(fig: go.Figure, title: str, height: int = 420) -> go.Figure:
    """Apply a consistent look-and-feel to any figure.

    Centralising theme tweaks means every chart shares fonts, background and
    margins - one place to change the whole dashboard's style.
    """
    fig.update_layout(
        title=title,
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        colorway=config.PALETTE,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    orientation: str = "v",
    text: str | None = None,
) -> go.Figure:
    """Horizontal/vertical bar chart helper."""
    fig = px.bar(
        data, x=x, y=y, color=color, orientation=orientation,
        text=text, color_discrete_sequence=config.PALETTE,
    )
    # Reduce clutter on the value axis; hover shows exact numbers.
    fig.update_traces(textposition="outside")
    return _apply_theme(fig, title)


def line_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    markers: bool = True,
) -> go.Figure:
    """Multi-series line chart helper (``color`` splits series)."""
    fig = px.line(
        data, x=x, y=y, color=color, markers=markers,
        color_discrete_sequence=config.PALETTE,
    )
    return _apply_theme(fig, title)


def scatter_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    size: str | None = None,
    hover_name: str | None = None,
    trendline: str | None = None,
) -> go.Figure:
    """Scatter plot helper with optional size/hover/trendline."""
    fig = px.scatter(
        data, x=x, y=y, color=color, size=size, hover_name=hover_name,
        trendline=trendline, color_discrete_sequence=config.PALETTE,
    )
    return _apply_theme(fig, title)


def pie_chart(data: pd.DataFrame, names: str, values: str,
              title: str) -> go.Figure:
    """Donut-style pie chart helper."""
    fig = px.pie(data, names=names, values=values, hole=0.4,
                 color_discrete_sequence=config.PALETTE)
    return _apply_theme(fig, title)


def box_chart(data: pd.DataFrame, x: str, y: str, title: str,
              color: str | None = None) -> go.Figure:
    """Box plot helper - good for showing distributions per category."""
    fig = px.box(data, x=x, y=y, color=color,
                 color_discrete_sequence=config.PALETTE)
    return _apply_theme(fig, title)


def heatmap(data: pd.DataFrame, title: str,
            height: int = 520) -> go.Figure:
    """Heatmap from a wide ``data`` frame (index=y, columns=x).

    ``data`` is expected to be already pivoted (rows=categories, cols=series).
    """
    fig = go.Figure(
        data=go.Heatmap(
            z=data.values,
            x=data.columns.tolist(),
            y=data.index.tolist(),
            colorscale="Reds",
            hoverongaps=False,
        )
    )
    return _apply_theme(fig, title, height=height)


def area_chart(data: pd.DataFrame, x: str, y: str, title: str,
               color: str | None = None) -> go.Figure:
    """Stacked area chart helper (cumulative-style trends)."""
    fig = px.area(data, x=x, y=y, color=color,
                  color_discrete_sequence=config.PALETTE)
    return _apply_theme(fig, title)


def show(fig: go.Figure) -> None:
    """Render a Plotly figure in Streamlit.

    Wrapped so analyses never import streamlit directly for plotting - if the
    rendering call ever needs to change, it changes here once (DRY).
    """
    import streamlit as st  # local import keeps this module importable headless

    st.plotly_chart(fig, width="stretch")
