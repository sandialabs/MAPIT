# Exercise 3: Material Loss

<br>

## Objective

 Gain familiarity with the notional material losses. This exercise will prepare you for using MAPIT to evaluate safeguards systems.

:::{caution}
This exercise assumes that you are familiar with MAPIT and can perform tasks discussed in the previous exercises; [exercise 1](exercise1.md) and [exercise 2](exercise2.md).
:::


---
## Problem setup
---




* Start this exercise by launching MAPIT, selecting the `SNL curated dataset` option, and loading the `Abrupt` dataset.
    * This tutorial starts by assuming you are at the main MAPIT interface

+++

* Select all the checkboxes for available statistical tests
  * A total of five (5) checkboxes should be checked

+++

* Next, configure the required parameters in the statistical box using the same parameters from exercise 1 and 2:
    * `MBP = 416`
    * `Iterations = 50`
      * If running on a lower performance device, try running with `Interations = 20`
    * `Analysis Element/Index`: **U**
    * `Temporal Offset`: ***Empty***

+++

* Set the measurement errors by pressing the <kbd>Select Errors</kbd> button. Choose **3%** for **all random and systematic errors**.  

+++

* Run MAPIT by pressing the <kbd>Run</kbd> button.

---
## Baseline data exploration
---



* Start by plotting the various statistical quantities (i.e. MUF, CUMUF, SEID, SITMUF, and Page's trend test)
  * Note that the results look similar to the `Normal` dataset.
  * MUF plot should look similar to the image below.

```{image} ./assets/exercise3/muf1.png
:class: bg-primary
:width: 100%
:align: center
```

<br>


* Continue by examining the fuel pins. Do so by selecting `Ground Truth Data` for the data type and `Fuel Pins (output)` for the location.
    * Here, `Ground Truth Data` refers to the true value of the fuel pins (output), which can never be observed in practice.
    * **Note** : There are many fuel pins that are generated at a fuel fabrication facility. Plotting `Fuel Pins (output)` could take several seconds depending on your hardware.
    * Your plot should look similar to the image below.



```{image} ./assets/exercise3/pins1.png
:class: bg-primary
:width: 100%
:align: center
```

<br>

* Notice that starting around 1010 hours material is removed for about the next 100 hours. However, the statistical quantities did not reflect this material loss.


---
## Explore impact of lower uncertainty
---



* Perform the calculations again using a value of **0.5%** for **all random and systematic errors**.
    * MAPIT does not need to be restarted. Simply press <kbd>Select Errors</kbd> and use the dropdown menus to select the new error values. Then press <kbd>Run</kbd>.

+++

* After MAPIT has run with the updated error values, try plotting the statistical quantities again. You should notice some observable changes have occurred.
    * MUF shows a distinct change during the material balance period in which the material loss occurs (see image below).
    * CUMUF, SEID, SITMUF, and Page's trend test on SITMUF should all exhibit changes due to the presence of the material loss.


```{image} ./assets/exercise3/muf2.png
:class: bg-primary
:width: 100%
:align: center
```

:::{note}
This example demonstrates the importance of precise measurement systems. This particular loss was too small to be reliably detected at the 3% uncertainty level.  
:::





## Summary

🎉 You have finished the third MAPIT exercise. 🎉

This exercise introduced concepts related to notional material loss. The abrupt material loss was originally not visible at the 3% measurement uncertainty level. However, after lowering the uncertainty, the change in MUF was clearly visible. This is an important phenomena in safeguards that must be considered when selecting measurement systems for key measurement points. In this exercise you:

* Explored MUF
* Used MAPIT to look at the ground truth data
* Explored the impact of measurement uncertainty

 Continue to [exercise 4](exercise4.md).
