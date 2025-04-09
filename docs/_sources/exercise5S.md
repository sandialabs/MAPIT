# Exercise 5 Solution

:::{note}
It's impossible for us to explore the entire potential solution space, so if you develop a better answer feel free to let us know!
:::

:::{note}
An error config for this setup can be found [here](./assets/exercise5/errorConfig.csv). Place this in the /MAPIT/src/ folder (so that it is in the same folder as `MAPIT.py`) which will enable loading the configuration in MAPIT using the `Load Error Config` after pressing the <kbd>Select Errors</kbd> button.
:::



### Cost


| Sensor | Quantity | Cost ($) |
|:---:|:---:|:---:|
| A | 0 | 0 |
| B | 26 | 260 |
| C | 0 | 0 |
| D | 3 | 90 |
| E | 2 | 150 |
| F | 0 | 200 |
| G | 0 | 0 |
| H | 0 | 0 |
| I | 0 | 0 |
| **Total Cost** | | **700** |




### Performance

Threshold: ($a_1 = 0.0$, $a_0 = 0.40$)

Values are approximate and may fluctuate to some degree. However, these values were calculated using 250 iterations, which should provide a relatively high level of certainty.

| False Alarm Probability (%) | Probability of Detection (%) |
|:---:|:---:|
| 5.0 | 76.3 |

![](./assets/exercise5s/SigmaMUF_Contribution_Normal.png)


+++

![](./assets/exercise5s/PageUonSITMUF1.png)



### Placement

| Location | Uncertainty (%) | Sensor |
|---|:---:|:---:|
Cylinder (input)| 0.5 | E
 Drums (input)| 1.0 | D
Vaporization| 5.0 | B
Precipitation| 5.0 | B
Offgas Filters| 5.0 | B
Centrifuge| 1.0 | D
CalcinationReduction| 5.0 | B
MillingBlending| 5.0 | B
Mixing Tank 1| 5.0 | B
Pressing| 5.0 | B
Sintering| 5.0 | B
Grinding| 5.0 | B
Pellet Storage| 5.0 | B
Tube Filling| 1.0 | D
ADU Scrap | 5.0 | B
Green Scrap| 5.0 | B
Dirty Powder| 5.0 | B
Sintered Scrap| 5.0 | B
Grinder Sludge| 5.0 | B
OffSpec Pellets| 5.0 | B
Scrap Grinder| 5.0 | B
Scrap Oxidation| 5.0 | B
Scrap Dissolution| 5.0 | B
Scrap Solvent| 5.0 | B
Scrap Precipitation| 5.0 | B
Scrap Grinder 2| 5.0 | B
Scrap Oxidation 2| 5.0 | B
Scrap Reduction  | 5.0 | B
UF6 Heel (output)| 5.0 | B
Fuel Pins (output)| 0.5 | E
Scrap Loss (output)| 5.0 | B
