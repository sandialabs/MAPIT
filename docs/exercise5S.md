# Exercise 5 Solution

> :information_source: It's impossible for us to explore the entire potential solution space, so if you develop a better answer feel free to let us know!

> :information_source: An error config for this setup can be found [here](../assets/exercise5/errorConfig.csv). Place this in the /MAPIT/src/ folder (so that it is in the same folder as `MAPIT.py`) which will enable loading the configuration in MAPIT using the `Load Error Config` after pressing the `Select Errors` button.

#### Cost
| Sensor | Quantity | Cost ($) |
|:---:|:---:|:---:|
| A | 26 | 260 |
| B | 2 | 50 |
| C | 1 | 30 |
| D | 2 | 150 |
| E | 0 | 0 |
| **Total Cost** | | 490 |


#### Performance
> Threshold = 2.1

>Values are approximate and may fluctuate to some degree. However, these values were calculated using 250 iterations, which should provide a relatively high level of certainty.

| False Alarm Probability (%) | Probability of Detection (%) |
|:---:|:---:|
| 4.8 | 72.4 |

#### Placement

| Location | Uncertainty (%) | Sensor |
|---|:---:|:---:|
Cylinder (input)| 0.5 | D
 Drums (input)| 1.0 | C
Vaporization| 5.0 | A
Precipitation| 5.0 | A
Offgas Filters| 5.0 | A
Centrifuge| 3.0 | B
CalcinationReduction| 5.0 | A
MillingBlending| 5.0 | A
Mixing Tank 1| 5.0 | A
Pressing| 5.0 | A
Sintering| 5.0 | A
Grinding| 5.0 | A
Pellet Storage| 5.0 | A
Tube Filling| 3.0 | B
ADU Scrap | 5.0 | A
Green Scrap| 5.0 | A
Dirty Powder| 5.0 | A
Sintered Scrap| 5.0 | A
Grinder Sludge| 5.0 | A
OffSpec Pellets| 5.0 | A
Scrap Grinder| 5.0 | A
Scrap Oxidation| 5.0 | A
Scrap Dissolution| 5.0 | A
Scrap Solvent| 5.0 | A
Scrap Precipitation| 5.0 | A
Scrap Grinder 2| 5.0 | A
Scrap Oxidation 2| 5.0 | A
Scrap Reduction  | 5.0 | A
UF6 Heel (output)| 5.0 | A
Fuel Pins (output)| 0.5 | D
Scrap Loss (output)| 5.0 | A
