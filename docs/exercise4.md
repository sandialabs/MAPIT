# Exercise 4: Quantifying probability of detection

<br>

#### Goal: Understand how MAPIT can be used to evaluate probability of detection.

> :information_source: So far, exercises have focused on exploring qualitative changes that are induced by changes in measurement uncertainty or material loss. This section will focus on developing quantitative metrics for safeguards performance.

> :exclamation: This exercise assumes that you are familiar with MAPIT and can perform tasks discussed in the previous exercises; [exercise 1](../docs/exercise1.md), [exercise 2](../docs/exercise2.md) and [exercise 3](../docs/exercise3.md).

---
## Problem setup
---





1. Start this exercise by launching MAPIT, selecting the `SNL curated dataset` option, and loading the `Normal` dataset.
  * This tutorial starts by assuming you are at the main MAPIT interface


2. Select all the options in the Tests/Uranium box
  * There should be four in total


3. Next, configure the required parameters in the statistical box using the same parameters from exercise 1 and 2:
  * `MBP = 416`
  * `Iterations = 50`
  * `Generic Element Index = empty`
  * `Temporal Offset = empty`


4. Set the measurement errors by pressing the `Select Errors` button. Choose **0.5%** for **all random and systematic errors**.  

5. Run MAPIT by pressing the `Run` button.

> :information_source: Recall from the lecture notes that safeguards statistical tests are often tuned to have an average of 5% false alarm probability per year. The next steps will use MAPIT functionality to determine this threshold for Page's trend test on SITMUF.

> :exclamation: The data provided in these examples are 6480 hours long, which translate to about 270 days (a reasonable estimate of an operational year). Therefore, one iteration is a single year of simulated operation. When using your own data, use caution in determining statistical thresholds if your datasets have different lengths of time.

---
## Determining statistical thresholds
---

6. Plot Page's trend test on SITMUF
  * This is labeled as `Page U SITMUF` in MAPIT
  * Plotting a quantity is necessary to use the threshold functionality


7. Use the `Statistical Thresholds` box to determine an appropriate threshold (i.e. 5% FAP)
  * This is performed by entering values in the `Enter Threshold` box
  * MAPIT returns the number of iterations that exceed this threshold
      * MAPIT operates on the entire dataset, not just the iterations that are plotted. This can be important in cases where many iterations are calculated and only a few are plotted.


8. Your threshold should be near 1.34
  * Due to the randomness of the calculations, your threshold might be slightly different
  * Increasing the number of iterations can help obtain a more precise estimate of the threshold
    * The uncertainty in the threshold itself should roughly decrease with sqrt(iterations).


---
## Evaluating probability of detection
---



9. Close and restart MAPIT. Again, select the `SNL curated dataset`. However, this time select the `Abrupt` dataset.


10. Select the same options from steps 2, 3, and 4 then run MAPIT.
  * Select all the options in the Tests/Uranium box
  * Select a value of **0.5%** for **all random and systematic errors**
  * `MBP = 416`
  * `Iterations = 50`
  * `Generic Element Index = empty`
  * `Temporal Offset = empty`


11. Plot Page's trend test on U SITMUF
  * This is labeled as `Page U SITMUF` in MAPIT


12. Enter in the previously determined threshold from (8.) to determine the probability of detection for this material loss.
  * The value should be approximately 69%

> :information_source: In this exercise, we changed the measurement uncertainties for all locations to be the same value. However, in practice, different measurement technologies are deployed based on safeguards need. On your own, try changing just some high impact measurement locations to 0.5% while leaving others at higher levels to see if you can reach similar results.

---

> :tada: Congrats :tada:

> You have finished the foruth MAPIT exercise. For an optional challenge, continue to [exercise 5](../docs/exercise5.md).
