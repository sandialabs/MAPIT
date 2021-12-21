# Exercise 5: System Optimization

<br>

## Goal: Optimized a hypothetical safeguards system.

> :information_source: Exercises so far have focused on guided examples of MAPIT functionality. Here, you will be working on your own to develop a notional safeguards system using a previously unconsidered example included in MAPIT. Solutions can be found [here](exercise5S.md).


---
## Objective
---

Start by loading the `SNL curated dataset` labeled `protracted loss`. Your goal is to determine the optimal uncertainties to obtain a **70% detection rate** and **5% false alarm probability** using Page's trend test on Uranium. Start with the baseline assumption of 3% measurement uncertainties.  

An optimal solution will consist of the cheapest set of sensors that can reach the goals stated above.

> :exclamation: For this example, we are neglecting that real world sensors will potentially have different random and systematic uncertainties. Instead, assume sensors have the same uncertainty for both values.

> :information_source: Make use of the `Save Error Config` and `Load Error Config` to more quickly perform analyses. For example, when determining the FAP for a particular sensor configuration, use the `Save Error Config` before quitting. Then, when evaluating the sensor setup, use `Load Error Config` to quickly load the sensor setup without having to manually enter uncertainties again.

> :information_source: For reference, there are 2 inputs, 26 inventories, and 3 outputs.

> :information_source: Try to use 100 iterations or more for better probability estimates

### Sensor costs

| Sensor | Uncertainty (%) | Cost ($) |
|:---:|:---:|:---:|
| A | 5.0 | 10 |
| B | 3.0 | 25 |
| C | 1.0 | 30 |
| D | 0.5 | 75 |
| E | 0.1 | 200 |

---
## Baseline solution
---

For the baseline assumption, it was assumed that all measurement locations have a 3% uncertainty, implying that only Sensor Cs were used.


### Cost

| Sensor | Quantity | Cost ($) |
|:---:|:---:|:---:|
| A | 0 | 0 |
| B | 31 | 775 |
| C | 0 | 0 |
| D | 0 | 0 |
| E | 0 | 0 |
| **Total Cost** | | **775** |




### Performance

>Threshold = 1.50

| False Alarm Probability (%) | Probability of Detection (%) |
|:---:|:---:|
| **4.8** | **6.4** |
