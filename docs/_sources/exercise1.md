# Exercise 1: General MAPIT Familiarity 

+++

## Objective 

The goal of this tutorial is to gain familiarity with basic MAPIT functionality.

:::{note}
Different stakeholders use different terminology for safeguards quantities. In some instances, the terms involve the same mathematical calculation even if the method to obtain the underlying data differs. MAPIT includes both "domestic" and "international" terminology. The following table shows terms that are mathematically equivalent. The operational and policy differences between the terms are not described here.

| Generic    | International | Domestic |
| -------- | ------- | ------- |
| MB |  MUF | ID |
| $\sigma$ MB | $\sigma$ MUF <br> SEMUF | $\sigma$ID <br> SEID |
|  - | SITMUF | - |
| - | Page's trend test | - |

:::

---

## Opening MAPIT 

---

* Start by launching MAPIT
  * If new to Python:
    * Windows: Run `run.bat` located in `\MAPIT\windows_scripts` by double clicking
    * Unix: Run `bash run.sh` in a console, ensuring that the current working directory is located in `\MAPIT\unix_scripts`
  * Otherwise:
    * Run MAPIT from you previously setup environment by running `MAPIT` from the command line.

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
  * MAPIT preferences regarding style and font size is stored internally and will be retained after closing MAPIT.
* If the exemplar data has not been downloaded from the [MAPIT tools](https://github.com/sandialabs/MAPIT-tools) repository do so now before proceeding.
  * If there are no options listed in the `Scenario Selection` box of the `Data` area, make sure the `Exemplar Data` box is checked and the `/path/to/data` is specified correctly in *File* > *Load Exemplar Data* > *Select directory*.

```{image} ./assets/scenescreenshots/MAPITmain2.png
:class: bg-primary
:width: 100%
:align: center
```

<br>

:::{note}
The status bar in the bottom left lets the user know what the GUI is doing at the moment. Initially when the GUI is opened it states waiting for problem setup. After data is imported, the analysis boxes are checked, statistical boxes are filled out, the simulated measurement error is specified, and <kbd>Run</kbd> is pressed, the bar will display the progress through the selected analyses. 

Once all of the analyses have been completed, the status bar states execution finished. At this point, the user is able to use the plot controls and statistical thresholds to plot the analyses and the base data.  The status bar, GUI animations, and tooltips are all used within MAPIT to help explain the safeguards analysis flow. Initially, the analyses and statistics boxes are highlighted in gold, which indicate those inputs are required for analysis.
:::

:::{note}
Currently, only options for statistical tests on uranium are available as it is the only element tracked in the fuel fabrication facility examples.
:::

---

## Performing a basic analysis

---

* Start by selecting `Normal` for `Scenario selection` if not already selected. 


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

* Setup errors by clicking the <kbd>Select Errors</kbd> button in the statistics box.
  * This opens the error selection pane
  * All errors are in percents
    * For example, a value of 1 is a 1% error
  * Options are provided to adjust measurement errors for various KMPs
  * Users can manually enter values in the boxes
  * Alternatively, the drop down boxes can change all values for that measurement type automatically
    * For example, all random input errors can be changed at once, or all systematic errors
  * Some error configurations can be tedious to input. Functionality is provided to save and load configurations using the <kbd>Load Error Config</kbd> and <kbd>Save Error Config</kbd> buttons.

:::{tip}
The default config directory can be found by using the `platformdirs` package as follows:
```python
from platformdirs import user_config_dir
print(user_config_dir("MAPIT",None))
```
:::


+++

* For now, select 1% errors for all values using the drop down options.

+++



* Press the <kbd>Run</kbd> button to run MAPIT



## Summary

In this exercise you learned the about the basic functionality of MAPIT:
- Opening MAPIT
- How to load included datasets
- How to run MAPIT
- How to input required parameters to run MAPIT



🎉 You have finished the first MAPIT exercise. 🎉

Continue to [exercise 2](exercise2.md).
