# Home

---

:::{versionadded} 1.5.0
   Added two variations of the GEMUF test; GEMUF-V1 and GEMUF-V5B3. The covariance matrix calculation has been refactored into a standalone calculation since MAPIT now supports several covariance-based tests. The statistical threshold in the GUI was also updated to support linear thresholds, since that is typically used for GEMUF tests.
:::

:::{versionadded} 1.4.6
   Added the capability to handle both continuous (e.g., signals) and discrete (e.g., entities) separately. The GUI will now prompt you to select the type of data you are analyzing. The API also includes a separate argument to handle the two types of data. See the API documentation for further details.
:::

:::{versionadded} 1.4.6
   Added the capability to specify a recalibration period. This effectively recalculates the systematic error periodically. This capability is available in the GUI (in the error specification pane) and the API. See the API documentation for further details.
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