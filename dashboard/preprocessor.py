"""Data cleaning and merging utilities.

Single Responsibility: turn raw frames into analysis-ready frames. Every
function here is *pure* (takes frames in, returns new frames out - it never
mutates its inputs), which makes the transformations predictable and reusable
across analyses (DRY).

The brief asks for "imports, merges, exploratory data analysis". Those all live
here so each analysis module can stay focused on presentation.
"""

from __future__ import annotations

import pandas as pd

from dashboard import data_loader as dl

# ---------------------------------------------------------------------------
# Basic cleaning helpers
# ---------------------------------------------------------------------------


def clean_results(results: pd.DataFrame) -> pd.DataFrame:
    """Return ``results`` with numeric columns coerced and a DNF flag added.

    The Ergast ``results.position`` column holds "\\N" for cars that did not
    finish, which pandas reads as ``object``. We coerce it to numeric so
    arithmetic works, and add an ``is_dnf`` boolean for easy filtering.
    """
    df = results.copy()

    numeric_cols = ["position", "positionOrder", "grid", "points", "laps",
                    "milliseconds", "fastestLapSpeed"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["is_dnf"] = df["position"].isna()

    # A clean, human-readable label like "P1", "P2" useful for plotting.
    df["position_label"] = df["position"].apply(
        lambda p: f"P{int(p)}" if pd.notna(p) else "DNF"
    )
    return df


def add_full_name(drivers: pd.DataFrame) -> pd.DataFrame:
    """Add a ``full_name`` column ("Forename Surname") to a drivers frame."""
    df = drivers.copy()
    df["full_name"] = (df["forename"].str.strip() + " " +
                       df["surname"].str.strip())
    return df


def parse_pit_duration(pit: pd.DataFrame) -> pd.DataFrame:
    """Return ``pit`` with a numeric ``duration_seconds`` column.

    The raw ``duration`` text comes in two shapes:
      - plain seconds, e.g. ``"26.898"``
      - minutes:seconds, e.g. ``"1:44.833"`` (for very slow stops)

    A naive ``astype(float)`` crashes on the second shape, so we instead derive
    seconds from the always-numeric ``milliseconds`` column. Centralising this
    in one helper keeps every caller correct (DRY).
    """
    df = pit.copy()
    # ``milliseconds`` is numeric in the dataset; divide to get seconds.
    df["duration_seconds"] = (
        pd.to_numeric(df["milliseconds"], errors="coerce") / 1000.0
    )
    return df


def attach_race_year(
    df: pd.DataFrame, races: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Merge the ``year`` column from races onto any frame with ``raceId``.

    Many analyses need the season year but the source dataset only has
    ``raceId``. This helper centralises that very common merge (DRY).
    """
    races = dl.load_races() if races is None else races

    year_map = races[["raceId", "year"]].drop_duplicates("raceId")
    return df.merge(year_map, on="raceId", how="left")


# ---------------------------------------------------------------------------
# Larger "star schema" assemblies (merged frames used by several analyses)
# ---------------------------------------------------------------------------


def build_results_fact(limit_years: tuple[int, int] | None = None) -> pd.DataFrame:
    """Build the main fact table: one row per driver-per-race.

    Joins ``results`` with races (year/race name), drivers (name/nationality)
    and constructors (team name/nationality). This single merged frame powers
    most of the analyses, so building it once avoids repeated merges.

    Parameters
    ----------
    limit_years:
        Optional ``(start, end)`` inclusive year filter to keep the frame
        small when a user narrows the season range. ``None`` keeps all years.
    """
    results = clean_results(dl.load_results())
    races = dl.load_races()
    drivers = add_full_name(dl.load_drivers())
    constructors = dl.load_constructors()

    if limit_years is not None:
        start, end = limit_years
        races = races[(races["year"] >= start) & (races["year"] <= end)]

    fact = (
        results
        # Keep race name + year.
        .merge(races[["raceId", "year", "name", "circuitId"]],
               on="raceId", how="inner")
        .rename(columns={"name": "race_name"})
        # Driver identity.
        .merge(drivers[["driverId", "full_name", "nationality"]],
               on="driverId", how="left")
        .rename(columns={"nationality": "driver_nationality"})
        # Team identity.
        .merge(
            constructors[["constructorId", "name", "nationality"]],
            on="constructorId", how="left",
        )
        .rename(columns={"name": "constructor_name",
                         "nationality": "constructor_nationality"})
    )
    return fact


def build_status_map() -> pd.DataFrame:
    """Return the status lookup table (statusId -> human status text)."""
    return dl.load_status()


# ---------------------------------------------------------------------------
# Exploratory helpers
# ---------------------------------------------------------------------------


def dataset_overview() -> pd.DataFrame:
    """Return a small DataFrame describing the datasets used by the app.

    Used on the Home page as an at-a-glance EDA: how many rows/columns each
    source file has and how many missing values it contains.
    """
    sources = {
        "races": dl.load_races,
        "results": dl.load_results,
        "drivers": dl.load_drivers,
        "constructors": dl.load_constructors,
        "circuits": dl.load_circuits,
        "status": dl.load_status,
    }
    rows = []
    for name, loader in sources.items():
        frame = loader()
        rows.append(
            {
                "Dataset": name,
                "Rows": len(frame),
                "Columns": frame.shape[1],
                "Missing values": int(frame.isna().sum().sum()),
            }
        )
    return pd.DataFrame(rows)
