"""Dataset loading layer.

Single Responsibility: this module *only* knows how to read CSV files from
disk. It does **not** clean, merge or transform anything (that is the job of
:mod:`dashboard.preprocessor`). Keeping I/O separate from transformation makes
both easy to test and reuse.

"only load the files you actually need". Because
every loader is a small function, an analysis requests just the datasets it
uses - nothing more.

``st.cache_data`` memorises results across Streamlit reruns. Without it every
widget interaction would re-read the (large) CSVs from disk.
"""

from __future__ import annotations

from functools import lru_cache

import pandas as pd
import streamlit as st

from dashboard.config import dataset_path


@lru_cache(maxsize=None)
def _read(name: str) -> pd.DataFrame:
    """Read a dataset by base name (uncached Streamlit primitive)."""
    path = dataset_path(name)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset '{name}.csv' not found in {path.parent}. "
            "Did you extract pl01_dataset.zip into ./datasets ?"
        )
    return pd.read_csv(path, na_values=["\\N"])


@st.cache_data(show_spinner=False)
def load_dataset(name: str) -> pd.DataFrame:
    """Return a (cached) copy of a dataset.

    A defensive ``.copy()`` is returned so callers can mutate the frame
    without corrupting the cache (a classic pandas caching pitfall).
    """
    return _read(name).copy()


# Thin, explicit wrappers -------------------------------------------------
def load_races() -> pd.DataFrame:
    return load_dataset("races")


def load_results() -> pd.DataFrame:
    return load_dataset("results")


def load_drivers() -> pd.DataFrame:
    return load_dataset("drivers")


def load_constructors() -> pd.DataFrame:
    return load_dataset("constructors")


def load_circuits() -> pd.DataFrame:
    return load_dataset("circuits")


def load_status() -> pd.DataFrame:
    return load_dataset("status")


def load_lap_times() -> pd.DataFrame:
    return load_dataset("lap_times")


def load_pit_stops() -> pd.DataFrame:
    return load_dataset("pit_stops")


def load_qualifying() -> pd.DataFrame:
    return load_dataset("qualifying")


def load_driver_standings() -> pd.DataFrame:
    return load_dataset("driver_standings")


def load_constructor_standings() -> pd.DataFrame:
    return load_dataset("constructor_standings")
