# Exercise 1: General MAPIT Familiarity

<br>

##### Goal: Gain familiarize with basic MAPIT functionality.


 ---

 ## Opening MAPIT

---

1. Start by launching MAPIT.
  1. First activate your environment, which has the packages listed in the [requirements](../requirements.txt) installed.
  2. Next, enter `python MAPIT.py` into your console
    * Alternatively, run `MAPIT.py` from an IDE

---

## Using the scenario selector

---

2. MAPIT will prompt for data to be analyzed. Select the `SNL curated dataset` option.
  * Selecting this option should bring you to the scenario selection screen (shown below)

<p align="center">
<img src="../assets/exercise1/sceneselect.png" width="50%" height="100%">
</p>

> :information_source: The scenario selection block provides tools to become familiar with the included datasets developed by SNL (based on IAEA STR-150). The datasets contain simulated data from key measurement points in material balance area 2.

3. Begin by starting the animated plots by pressing the play button, ![](../assets/codeAssets/play.png), in the top right of the window.
  * Note that MAPIT shows an animated plot of the time-dependent behavior of several key measurement points.
  * A description for the default scenario, 'Normal', is provided in the middle window.
  * Press the pause button, ![](../assets/codeAssets/pause.png), when finished.

<br>

4. Try adjusting the sliders for the animation start and stop times. Note that the behavior repeats regardless of the selected window. This is expected for normal facility operation.

5. When finished, press the button labeled `Load data and Return to Plots`

---

## MAPIT main interface

---

6. The main window of MAPIT should now be shown (see below for light theme example)
  * MAPIT has both light and dark themes available
    * These can be toggled at any time using the `theme` dropdown menu

<p align="center">
<img src="../assets/exercise1/MAPITmain.png" width="50%" height="100%">
</p>

> :information_source: The status bar in the bottom left, progress bar in the bottom right, GUI animations, and tooltips are all used within MAPIT to help understand the safeguards analysis flow. Initially, the tests and statistics boxes are highlighted in blue, which indicate those inputs are required for analysis. Further, note the status bar which is waiting for the calculation setup.


> :pushpin: **Note** :pushpin:  Currently, only options for statistical tests on uranium are available as it is the only element tracked in the fuel fabrication facility examples.

7. Continue by selecting all the checkboxes for available statistical tests on uranium.
  * A total of four (4) checkboxes should be checked


8. Next, configure required parameters in the statistical box.
  * `MBP = 416`
    * MBP is the material balance period
    * For this exercise, the MBP least common multiple of the facility's input and output stream period
  * `Iterations = 50`
    * The number of realizations to run.
    * Note that in practice, only a single iterations would be observable.
  * `Generic Element Index = empty`
    * MAPIT can perform statistical tests on general datasets (i.e. not just uranium and plutonium)
    * In such scenarios, information must be provided about the element in the dataset that tests should be performed on
  * `Temporal Offset = empty`
    * In some cases, it may be desirable to ignore a startup period
    * The offset rebases the calculations to a new zero


10. Setup errors by clicking the `Select Errors` button in the statistics box.
  * This opens the error selection pane
  * All errors are in percents
    * For example, a value of 1 is a 1% error
  * Options are provided to adjust measurement errors for various KMPs
  * Users can manually enter values in the boxes
  * Alternatively, the drop down boxes can change all values for that measurement type automatically
    * For example, all random input errors can be changed at once, or all systematic errors
  * Some error configurations can be tedious to input. Functionality is provided to save and load configurations using the `Load Error Config` and `Save Error Config` buttons.


11. For now, select 1% errors for all values using the drop down options.

12. Press the run button to run MAPIT

---

> :tada: Congrats :tada:

> You have finished the first MAPIT exercise. Continue to [exercise 2](../docs/exercise2.md)

> You have finished the first MAPIT exercise. Continue to [exercise 2](/docs/exercise2.md)

> You have finished the first MAPIT exercise. Continue to [exercise 2](docs/exercise2.md)

> You have finished the first MAPIT exercise. Continue to [exercise 2](exercise2.md)

> You have finished the first MAPIT exercise. Continue to [exercise 2](../assets/codeAssets/pause.png)

> You have finished the first MAPIT exercise. Continue to [exercise 2](/assets/codeAssets/pause.png)

> You have finished the first MAPIT exercise. Continue to [exercise 2](assets/codeAssets/pause.png)
