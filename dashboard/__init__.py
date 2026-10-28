"""Formula 1 analytics dashboard package.

The package is organised by responsibility so that ``main.py`` stays a thin
entry point:

- :mod:`dashboard.config`        -> constant values (paths, theme, colours)
- :mod:`dashboard.data_loader`   -> reading CSV files (with caching)
- :mod:`dashboard.preprocessor`  -> cleaning / merging / normalising data
- :mod:`dashboard.components`    -> reusable Streamlit UI building blocks
- :mod:`dashboard.charts`        -> reusable Plotly chart builders
- :mod:`dashboard.analyses`      -> one module per analysis + a registry
"""