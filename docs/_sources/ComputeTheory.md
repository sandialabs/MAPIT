# Special computational considerations

## Numerical Integration

Inputs and outputs are currently assumed by MAPIT to be flows although a future update will better support discrete items. That is, their units are represented as mass/time. It is assumed that flows will be represented in a continuous space as a non-zero value when the flow is on and zero (or near-zero) when off. These signals must be subsequently integrated to be used as input and/or output terms in the material balance. A routine called `trapSum` performs this task in MAPIT and is described in more detail below.

An important consideration when recording data is the sample frequency. If the sample frequency is very large (i.e., sampled infrequently) then the resulting data stream might not have recorded key flow events. Very small sample frequencies (i.e., sampled frequently) will capture all relevant events, but will result in a large, potentially sparse, dataset. The F3M library has specific blocks that implements an appropriate sample frequency if the F3M framework is being used. Solver step size for simulated models can also have a similar impact; large steps can result in key events being stepped over but small steps can result in a computationally expensive calculation. Keep data sample frequency and model simulation step size in mind when generating data for use within MAPIT.

### trapSum

`MAPIT.core.AuxFunctions.trapSum` is a function within MAPIT that attempts to numerically integrate a segment of data. The function expects that an array of boolean values is supplied which indicates if a region is to be integrated, along with the time step information, effective zero value (i.e., if a signal's off condition is not zero), and finally the data itself.

```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:lines: 42-46
:language: python
:linenos:
:lineno-start: 42
:caption: First, the function attempts to find the left and right indices that are relevant for the requested integration. Next, the data is sliced into the relevant segment.
```

```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:lines: 61-65
:language: python
:linenos:
:lineno-start: 61
:caption: If the requested segment has a non-zero signal before and/or after this segment note it (i.e., the first and final time steps are not zero)
```

The function attempts to find index pairs that represent a pulse of material. For example, if a tank fills and empties within the interval to integrate, it will have a geometric shape. The shape will depend on the flow rate to/from the tank, but it generally be a piecewise discontinuous shape (i.e., a pulse). The function generates a boolean mask for locations where the data is zero and non-zero, the intersection of which can be used to find segments of non-zero data.

```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:lines: 75-85
:language: python
:linenos:
:lineno-start: 75
:caption: Generate the left and right indices of non-zero data segments using the intersection of zero and non-zero values. 
```

Next, if there is a "partial" segment, that is a segment that stretches outside the bounds of the integration window, that case should be handled. This involves injecting some indices manually depending on what segments have been found so far. There's some additional checks to look for errors we have seen in Simulink, and to remedy them if present. 

Finally numerical trapezoidal integration is performed on each segment found in the integration window:

```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:lines: 205-211
:language: python
:linenos:
:lineno-start: 205
```