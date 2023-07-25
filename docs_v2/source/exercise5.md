# Exercise 5: System Optimization

<br>

## Goal

Optimized a hypothetical safeguards system.

:::{note}
Exercises so far have focused on guided examples of MAPIT functionality. Here, you will be working on your own to develop a notional safeguards system using a previously unconsidered example included in MAPIT. Solutions can be found [here](exercise5S.md).
:::




---
## Objective
---

Start by loading the `SNL curated dataset` labeled `protracted loss`. Your goal is to determine the optimal uncertainties to obtain a **70% detection rate** and **5% false alarm probability** using Page's trend test on Uranium. Start with the baseline assumption of 3% measurement uncertainties.  

An optimal solution will consist of the cheapest set of sensors that can reach the goals stated above.

:::{note}
For this example, we are neglecting that real world sensors will potentially have different random and systematic uncertainties. Instead, assume sensors have the same uncertainty for both values.
:::

:::{tip}
* Make use of the `Save Error Config` and `Load Error Config` to more quickly perform analyses. For example, when determining the FAP for a particular sensor configuration, use the `Save Error Config` before quitting. Then, when evaluating the sensor setup, use `Load Error Config` to quickly load the sensor setup without having to manually enter uncertainties again.
+++
* For reference, there are 2 inputs, 26 inventories, and 3 outputs.
+++
* Try to use 100 iterations or more for better probability estimates
:::




### Sensor costs



| Sensor | Uncertainty (%) | Cost ($) |
|:---:|:---:|:---:|
| A | 10.0 | 5 |
| B | 5.0 | 10 |
| C | 3.0 | 25 |
| D | 1.0 | 30 |
| E | 0.5 | 75 |
| F | 0.1 | 200 |
| G | 0.05 | 500 |
| H | 0.01 | 1000 |
| I | 0.005 | 2000 |

---
## Baseline solution
---

For the baseline assumption, it was assumed that all measurement locations have a 3% uncertainty, implying that only Sensor Bs were used.


### Cost

| Sensor | Quantity | Cost ($) |
|:---:|:---:|:---:|
| A | 0 | 0 |
| B | 0 | 0 |
| C | 31 | 775 |
| D | 0 | 0 |
| E | 0 | 0 |
| F | 0 | 0 |
| G | 0 | 0 |
| H | 0 | 0 |
| I | 0 | 0 |
| **Total Cost** | | **775** |




### Performance

>Threshold = 1.50

| False Alarm Probability (%) | Probability of Detection (%) |
|:---:|:---:|
| **4.8** | **6.4** |


When finished, compare against our solution, which can be found [here](exercise5S.md).