"""Central configuration.

Every magic value (file paths, colours, page settings) lives here so that the
rest of the code never hard-codes them. This follows the "single source of
truth" idea and makes the dashboard easy to re-theme or re-point.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

# ------------------------------------------------------------------ paths
# ``config.py`` sits in ``dashboard/`` so its parent's parent is the project
# root that contains the ``datasets`` folder. Building the path from the file
# location (instead of the current working directory) keeps imports working no
# matter where ``streamlit run`` is launched from.
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DATASETS_DIR: Path = PROJECT_ROOT / "datasets"


def dataset_path(name: str) -> Path:
    """Return the absolute path of a CSV dataset given its base ``name``.

    Centralising path building means every loader calls ``dataset_path("races")``
    instead of concatenating strings in many places (DRY).
    """
    return DATASETS_DIR / f"{name}.csv"


# ------------------------------------------------------------------ app meta
APP_TITLE: str = "Formula 1 Analytics"
APP_ICON: str = "🏎️"
APP_LAYOUT: Literal["centered", "wide"] = "wide"

# ------------------------------------------------------------------ theme
F1_RED: str = "#E10600"
NAVY: str = "#15151E"
SILVER: str = "#C0C0C0"
GOLD: str = "#FFD700"
PALETTE: list[str] = [
    "#E10600",  # F1 red
    "#1F77B4",
    "#2CA02C",
    "#FF7F0E",
    "#9467BD",
    "#8C564B",
    "#17BECF",
    "#7F7F7F",
]

# ------------------------------------------------------------------ media
# Multimedia assets. Remote URLs keep the repo lightweight and always render.
F1_LOGO_URL: str = (
    "https://upload.wikimedia.org/wikipedia/commons/3/33/F1.svg"
)
# A looping-free hero GIF hosted on a stable public CDN.
HERO_GIF_URL: str = (
    ".\\assets\\f1.gif"
)
