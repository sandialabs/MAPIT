# API home

:::{versionadded} 1.40.0
Added parallel capabilities. Note that we do not yet provide guidance on optimal settings for parallel batching.
:::

:::{versionchanged} 1.40.0
API breaking changes! Instead of accessing statistical tests directly, a new object, `MBArea`, is the preferred way to perform analyses using the API. The `StatsTests` module is provided for educational purposes only and it is expected that users instead user `MBArea` functions. See the API example notebooks for more details.
:::

```{toctree}
:maxdepth: 4
:glob:
:caption: Contents:
code_autogen/coreLanding
```