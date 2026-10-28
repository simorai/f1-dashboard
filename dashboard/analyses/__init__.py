"""Analysis package: one module per analysis + a central registry.

Design notes (SOLID):
- Each analysis module exposes a single ``render()`` function (Single
  Responsibility).
- The dashboard *depends on an abstraction* (a title + a callable), not on the
  concrete modules (Dependency Inversion).
- New analyses can be added without touching ``main.py``'s routing logic -
  just append to :data:`dashboard.analyses.ANALYSES` (Open/Closed).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from dashboard.analyses import (
    analysis_01_wins,
    analysis_02_points_evolution,
    analysis_03_pit_stops,
    analysis_04_dnf,
    analysis_05_qualifying,
    analysis_06_grid_to_finish,
    analysis_07_lap_times,
    analysis_08_drivers_map,
)


@dataclass(frozen=True)
class Analysis:
    """Immutable descriptor for one dashboard page.

    ``slug``     -> unique id used for navigation / query params.
    ``title``    -> label shown in the sidebar and page header.
    ``icon``     -> emoji shown in navigation (multimedia/polish).
    ``subtitle`` -> one-line description shown under the title.
    ``render``   -> zero-argument callable that draws the page.
    """

    slug: str
    title: str
    icon: str
    subtitle: str
    render: Callable[[], None]

ANALYSES: list[Analysis] = [
    Analysis(
        slug="wins",
        title="Most Race Wins",
        icon="🏆",
        subtitle="Which constructors and drivers have won the most races?",
        render=analysis_01_wins.render,
    ),
    Analysis(
        slug="points",
        title="Points Evolution",
        icon="📈",
        subtitle="How has the points total of top teams evolved per season?",
        render=analysis_02_points_evolution.render,
    ),
    Analysis(
        slug="pit_stops",
        title="Pit Stop Performance",
        icon="🔧",
        subtitle="Which teams execute the fastest pit stops?",
        render=analysis_03_pit_stops.render,
    ),
    Analysis(
        slug="dnf",
        title="Reliability / DNFs",
        icon="🛑",
        subtitle="Why do drivers fail to finish races?",
        render=analysis_04_dnf.render,
    ),
    Analysis(
        slug="qualifying",
        title="Qualifying vs Race",
        icon="⏱️",
        subtitle="Does a strong qualifying position translate into race points?",
        render=analysis_05_qualifying.render,
    ),
    Analysis(
        slug="grid",
        title="Grid to Finish",
        icon="🚦",
        subtitle="How many positions do drivers gain or lose from the grid?",
        render=analysis_06_grid_to_finish.render,
    ),
    Analysis(
        slug="lap_times",
        title="Lap Time Analysis",
        icon="🔄",
        subtitle="Lap-by-lap pace of a selected race.",
        render=analysis_07_lap_times.render,
    ),
    Analysis(
        slug="map",
        title="Drivers on a Map",
        icon="🌍",
        subtitle="Geographic distribution of drivers by nationality.",
        render=analysis_08_drivers_map.render,
    ),
]


def get_analysis(slug: str) -> Analysis:
    """Look up an analysis by slug, falling back to the first one.

    Dependency Inversion: callers ask for an ``Analysis`` object rather than
    importing concrete modules directly.
    """
    for analysis in ANALYSES:
        if analysis.slug == slug:
            return analysis
    return ANALYSES[0]
