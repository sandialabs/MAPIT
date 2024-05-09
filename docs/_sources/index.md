# Home

---

:::{versionchanged} 1.40.0
   API breaking changes! Instead of accessing statistical tests directly, a new object, ``MBArea``, is the preferred way to perform analyses using the API. The ``StatsTests`` module is provided to show implementation details, but it is expected that users instead user ``MBArea`` functions. See the API example notebooks for more details.
:::

MAPIT (Material Accountancy Performance Indicator Toolkit) is a Python package designed to aid in safeguards analysis of bulk materials. The inherent flexibility is designed to allow safeguards practitioners ask the "what if?" questions while providing transparency into commonly employed statistical tests. 

MAPIT provides both a graphical user interface (GUI) and an application program interface (API). The API can be used with other popular Python libraries to extend functionality and integrate with other analytical workflows. 



:::{subfigure} AB
:subcaptions: above
:class-grid: outline
![](/assets/screenshots/MAPIT_split3.png)
![](/assets/screenshots/mapit_api_ex.png)
:::

```{toctree}
:maxdepth: 1
:glob:
:caption: Contents:
self
install
tutorials
guided_exercises
theory
apidocs
```

## Acknowledgements



```{image} ./assets/screenshots/MPACT_Logo.jpg
:class: bg-primary
:width: 50%
:align: right
```
<br>

This work is supported by the DOE/NE Office of Materials and Chemical Technologies (NE-43) - Materials Protection, Accounting, and Control Technologies (MPACT) program.