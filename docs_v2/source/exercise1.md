# Exercise 1: General MAPIT Familiarity 

+++

## Objective 

The goal of this tutorial is to gain familiarity with basic MAPIT functionality.


---

## Opening MAPIT 

---

* Start by launching MAPIT
  * If new to Python:
    * Windows: Run `run.bat` located in `\MAPIT\windows_scripts` by double clicking
    * Unix: Run `bash run.sh` in a console, ensuring that the current working directory is located in `\MAPIT\unix_scripts`
  * Otherwise:
    * Run MAPIT from you previously setup environment

:::{tip}
If you are having trouble viewing MAPIT on your screen, try maximizing the window. 
:::

---

## MAPIT main interface

---



* The main window of MAPIT should now be shown (see below for light theme example)
  *   MAPIT has both light and dark themes available
      *   These can be toggled at any time using the `Theme` dropdown menu
  *   MAPIT allows users to control the font size
      *   The fontsize can be changed using the `Accessibility` dropdown menu 

```{image} ./assets/exercise1/MAPITmain.png
:class: bg-primary
:width: 100%
:align: center
```

<br>

:::{note}
The status bar in the bottom left lets the user know what the GUI is doing at the moment. Initially when the GUI is opened it states waiting for problem setup. After the analysis boxes are checked, statistical boxes are filled out, the simulated error bars are chosen, and run is pressed the bar will display the progress through the selected analyses. Once all of the analyses have been complete, the status bar states execution finished. At this point, the user is able to use the plot controls and statistical thresholds to plot the analyses and the base data.  The Status bar, GUI animations, and tooltips are all used within MAPIT to help understand the safeguards analysis flow. Initially, the analyses and statistics boxes are highlighted in gold, which indicate those inputs are required for analysis.
:::

:::{note}
Currently, only options for statistical tests on uranium are available as it is the only element tracked in the fuel fabrication facility examples.
:::

---

## Using the scenario selector

---



MAPIT first column is broken into sections. The first titled Data will prompt the user to select a SNL curated dataset or load their own dataset. Under `Model selection` option ensure the fuel fab model is selected and under `Scenario selection` select the Normal dataset. Clicking the `Scenario Explorer` should bring you to the following pop-up (shown below).

<!-- <p align="center">
<img src="./assets/exercise1/sceneselect.png" width="100%" height="100%">
</p> -->


```{image} ./assets/exercise1/sceneselect.png
:class: bg-primary
:width: 100%
:align: center
```

<br>

:::{note}
The scenario selection block provides tools to become familiar with the included datasets developed by SNL (based on IAEA STR-150). The datasets contain simulated data from key measurement points in material balance area 2.
:::

+++


* Begin by starting the animated plots by pressing the play button, ![](./assets/codeAssets/play.png), in the top right of the window.
  *   Note that MAPIT shows an animated plot of the time-dependent behavior of several key measurement points.
  *   A description for the default scenario, 'Normal', is provided in the middle window.
    *   Press the pause button, ![](./assets/codeAssets/pause.png), when finished viewing the animation. 

+++

* Try adjusting the sliders for the animation start and stop times. Note that the behavior repeats regardless of the selected window. This is expected for normal facility operation.

+++

* When finished, close the pop-up.



* Continue by selecting the checkboxes for the following statistical tests.
  * MUF
  * Cumulative MUF
  * Sigma MUF
  * SITMUF
  * Page's test on SITMUF

+++

* Next, configure required parameters in the statistical box:
  * `MBP`: **416**
    * MBP is the material balance period
    * For this exercise, the MBP least common multiple of the facility's input and output stream period
  * `Iterations`: **50**
    * The number of realizations to run.
    * Note that in practice, only a single iterations would be observable.
    * If running on a lower performance device, try running with `Interations`: **20**
  * `Analysis Element/Index`: **U**
    * MAPIT can perform statistical tests on general datasets (i.e. not just uranium and plutonium)
    * In such scenarios, information must be provided about the element in the dataset that tests should be performed on
  * `Temporal Offset`: ***Empty***
    * In some cases, it may be desirable to ignore a startup period
    * The offset rebases the calculations to a new zero

+++

* Setup errors by clicking the `Select Errors` button in the statistics box.
  * This opens the error selection pane
  * All errors are in percents
    * For example, a value of 1 is a 1% error
  * Options are provided to adjust measurement errors for various KMPs
  * Users can manually enter values in the boxes
  * Alternatively, the drop down boxes can change all values for that measurement type automatically
    * For example, all random input errors can be changed at once, or all systematic errors
  * Some error configurations can be tedious to input. Functionality is provided to save and load configurations using the `Load Error Config` and `Save Error Config` buttons.

+++

* For now, select 1% errors for all values using the drop down options.

+++

:::{note}
The datasets are not loaded until the simulated error is set for the dataset.
:::

* Press the run button to run MAPIT



## Summary

In this exercise you learned the about the basic functionality of MAPIT:
- Opening MAPIT
- How to load included datasets
- How to run MAPIT
- How to input required parameters to run MAPIT



🎉 You have finished the first MAPIT exercise. 🎉

Continue to [exercise 2](exercise2.md).
