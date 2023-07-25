# MAPIT Introduction

## Fuel fabrication overview

The purpose of this tutorial is to introduce you to the included example dataset. This dataset was based on a fuel fabrication facility described by [IAEA-STR150](https://inis.iaea.org/search/search.aspx?orig_q=RN:17037216). There are some unique features of MAPIT that are only present when using the included datasets.

Some information about the fuel fabrication facility is noted below:
* 300 MT UO$_2$
* 3.0% weight percent $^{235}$U
* Final products are LWR fuel assemblies
* Feed material:
  * Low enriched UF$_6$
  * Uranyl nitrate
  * UO$_2$ powder
  * Material from facility scrap recovery


## Walkthrough

This tutorial describes basic functions of MAPIT and how to get started using the sample dataset that has been included.

:::{note}
This tutorial contains notes that are not necessary to understand the tool's basic functionality, but may be useful to users looking for more advanced functionality.
:::



## Getting started
### Loading the included dataset
The pre-generated dataset described in the introduction can be accessed by selecting `SNL curated dataset` button when MAPIT is first loaded and prompts for data to be analyzed. This will open the scenario examiner area. The scenario examiner enables a detailed look of MBA2 of the fuel fabrication facility described in [IAEA-STR150](https://inis.iaea.org/search/search.aspx?orig_q=RN:17037216).

It is often difficult to envision individual unit processes at a facility and how they relate to the over safeguards setup. The scenario examiner area has several drop down menus that enable animated plots showing the inventory behavior of various unit operations. Use this area before selecting the `Load data and return to plots` button to gain an intuition of the fuel fabrication facility's normal operation.

:::{note}
This dataset only has data for Uranium. Selecting some of the other interactive plot options such as Plutonium or Xenon will plot a series of zeros. Future updates may add another scenario for reprocessing under the PUREX tab which would include these elements.
:::



After selecting `Load data and return to plots` you will be returned to the main MAPIT area where other options will be available (highlighted in blue - see below).

:::{note}
Importing data only needs to be performed once. You can repeat the following steps below multiple times without needing to import the data again. For example, changing the simulated error can be done by selecting `Select Errors` followed by `Run`. 
:::


```{image} ./assets/scenescreenshots/MAPITmain2.png
:class: bg-primary
:width: 100%
:align: center
```
<br>







### Statistical test configuration
The boxes with blue borders are the next steps in the MAPIT workflow. The currently available statistical tests are denoted by check boxes, go ahead and select all of them.




The suggest parameters for the statistics parameters are as follows:

  * `MBP` (Material Balance Period, units of hours) : **320**
  * Try different `MBP` lengths to see how performance statistics change
  * `Iterations` (Number of statistical realizations to run): **100**
    * Increasing the number of `Iterations` can reduce the simulation uncertainty in the probability of detection
  * `Generic Element Index`: ***Empty***
  * `Temporal Offset`: ***Empty***


After setting the required statistics inputs the final step before starting the calculation is setting the errors. As no measurements are perfect it is impossible to know the true value of some quantity of interest (in this case Uranium) at a particular location. Use `Select Errors` to open an interactive dialog to set measurement errors. These can be set individually or as a group. Press `Done` when finished.



:::{tip}
One purpose of MAPIT is to understand how these errors impact common safeguards statistical tests, so feel free to choose any value. The [IAEA ITV](https://inis.iaea.org/search/search.aspx?orig_q=RN:49058823) (International Target Values) provides a good reference for expected performance for different types of measurement systems.
:::

<!-- :::{note}
MAPIT has values listed for U, Pu, and Generic measurement errors. For this tutorial, the Pu and Generic measurement errors serve no purpose as we are only interested in Uranium. However, there may be situations where you want to analyze Uranium, Plutonium, or perhaps some arbitrary element ("Generic") all at once with the same measurement system. The system may have different performance based on the element, hence the flexibility for multiple error specifications.
::: -->



:::{tip}
Entering a customized error table can be tedious. The included example scenario has 31 different measurement locations! MAPIT allows for loading (`Load Error Config`) that reads a .csv table of errors so that manual specification is not required every time MAPIT is run. Similarly, you can use (`Save Error Config`) to save a specified error configuration to disk.
:::



### Analysis
Once the statistical tests and errors have been configured press `Run` to start the calculation. MAPIT is a lightweight tool that should run fairly quickly for a small number of iterations (~100), but varies based on hardware configuration. Progress can be monitored through the dialog and progress bar at the bottom of the tool (see below).


```{image} ./assets/scenescreenshots/progress1.png
:class: bg-primary
:width: 100%
:align: center
```

<br>



#### Plotting


The first step in many analytical workflows is to plot data to gain an intuition for what is happening. MAPIT has multiple plot options (shown below) that dynamically change based on the option selected. Try plotting different quantities of interest (also make sure to note how these change with the selected errors).

```{image} ./assets/scenescreenshots/plot1.png
:class: bg-primary
:width: 25%
:align: center
```

<br>



The various options are as follows:

* **Plot Data Type**
  * Varies depending on selected statistical tests
  * Always includes the "ground truth data" and "observed data"
    * Ground truth is the data before errors are applied by MAPIT
    * Observed data is the ground truth after errors have been applied
  * Requested statistical tests will also be available here
* **Plot Data Location**
  * Only relevant for "ground truth data" and "observed data"
    * Location doesn't apply to the statistical tests at the moment as MAPIT only supports analysis of one material balance area at a time
  * Lists locations based data used
    * Included dataset has locations baked in
    * Attempts to use user provided locations if data was imported
* **Plot Data Nuclide**
  * Only relevant for "ground truth data" and "observed data"
  * Used to plot specific nuclide at a location of interest within the material balance
* **Iterations to Plot**
  * Not relevant for "ground truth data"
  * Used to control how many iterations are plotted

#### Thresholds
Statistical tests used in safeguards usually require adjustment of at least one tunable parameter. For example, Page's trend test actually has two (h and k) of which one is made available to users (h).

:::{important}
Page's trend test currently uses k=0 which is the ideal statistic for a one unit shift in SITMUF
:::



The statistical threshold area of MAPIT (shown below) allows users to input a value and see how many times that threshold has been crossed. The threshold calculation is generic and can be applied to any of the plot quantities.

```{image} ./assets/scenescreenshots/Thresh1.png
:class: bg-primary
:width: 25%
:align: center
```

<br>

:::{note}
The quantity reported by MAPIT `% Above Threshold` reflects *all* of the runs, even if not plotted. For example, if 1000 iterations were requested, then the max quantity of iterations allowed to be plotted at once is 100. However, the threshold will check all 1000 runs and report the quantity that exceeds the threshold.
:::

:::{note}
The threshold tool reports if a particular iteration of a quantity of interest has past the threshold at *any* time in the dataset. There may be some desire to check a threshold for a limited window of time, however this capability is not yet implemented. In the meantime, please preprocess your data if desired to circumvent this limitation. For example, if you want to know yearly performance, but your dataset is two years long, split the dataset in half before importing into MAPIT.
:::




#### Error contributions
Understanding the contribution of various facility measurements to the material balance uncertainty is often important. Identifying large sources of error can help prioritize areas for improvement. MAPIT facilitates this analysis by providing tabular data describing the error contribution of various components. This can be accessed through the `Tabular Data View` menu in the main MAPIT area and selecting `Error Contribution`.


#### Data Export
While MAPIT has a wide range of capabilities it may be desirable to save data for secondary analysis or use with a report. MAPIT supports saving of figures generated in the plot area in addition to the raw data itself.

#### Figure
Figure can be saved in one of two different ways:
* First (recommended) use the save icon at the bottom of the plot (see below) which directly interacts with the [Matplotlib](https://matplotlib.org/) backend.
* Second (not recommended), you can use the `Figure Options` in the main MAPIT area and select one of the `Save Figure` options.




* Plots can be further customized using the options on the navigation bar at the bottom of the plot (see below for an image of the navigation bar). 

```{image} ./assets/scenescreenshots/navi1.png
:class: bg-primary
:width: 40%
:align: center
```

<br>







#### Data
The data can be exported by selecting the `File` menu option in the MAPIT main area and selecting `Save Data`. An option will be presented to save the underlying data used for the safeguards statistical tests (i.e. "observed data"). The default behavior is to save data in `.csv` format with a shape of [time x iterations]. For example, for a case where 100 iterations were requested and the time was 5000, then the `.csv` would be of shape `(5000,100)`.

:::{important}
The default behavior is to create a folder called "MAPIT_Output" containing output files in the same location where `MAPIT.py` is located.
:::

:::{caution}
Do not expect reliable performance of this capability when using irregularly sampled data. Although MAPIT can handle this type of data, validation efforts are ongoing and have not yet been completed.
:::

