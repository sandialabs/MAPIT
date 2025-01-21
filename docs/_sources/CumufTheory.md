# CuMUF

## Historical context 
Cumulative MUF (CuMUF) is the sum of all MUF values over a given period of time. The CuMUF test is noteworthy due to power to detect protracted losses. CuMUF in particular is strong in detecting protracted losses that occur early in the material balance sequence, but performs worse if the loss occurs later in the sequence. 

:::{note}
CuMUF is not the same as MUF cusum. MUF cusum is not currently implemented explicitly in MAPIT, but can be constructed using the API.
:::

## Theory

The CuMUF metric is calculated as follows:

$$
    \mathrm{CuMUF}_i  = \sum_{t=0}^i \mathrm{muf}_t
$$

## Discussion
The CuMUF statistic is often combined with statistical testing. The most straightforward test is a simple comparison to a critical value. That is, an alarm is triggered if CuMUF rises above a specific value. CuMUF can also be used with other trend methods like control charts or further extended to develop the cusum test.

:::{note}
CuMUF is the optimal statistical for detecting the worst-case loss. The worst-case loss, as originally derived by Avenhaus and Jaech, is the loss for which detection probability is minimized for the optimal statistical test. The worst-case loss was shown to be a loss wherein the per-balance loss is proportional to the row sums of the covariance of the material balance sequence. Note that this loss is the worst-case for any statistical test as it was derived using the assumption that the optimal statistical test for detection of a loss could be known and applied.
:::

## Implementation
:::{important}
Note that this function is not intended to be used standalone through direct calls, rather, it is designed to be called through the `MBArea` class of `StatsProcessor`. 
:::

The CuMUF statistic calculation is relatively straightforward and requires a minimal amount of code. The MUF array is a 2D array with shape (iterations, time steps) where time steps is on a per unit time basis. First, a [discrete 1D difference](https://numpy.org/doc/stable/reference/generated/numpy.diff.html) is performed on the MUF array to determine the location of unique MUF value. Those locations are stored to the array `idxs`.

```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 336-337
:language: python
:linenos:
:lineno-start: 336
```

The CuMUF statistic is then calculated for the sequence of MUF values. The resulting statistic is tiled across time steps to again result in a 2D array with shape (iterations, time steps). Without tiling, the shape would be (iterations, number of balance periods). After calculation, the array of statistics is returned.

```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 345-347
:language: python
:linenos:
:lineno-start: 345
```


## Further reading
* [Revisiting statistical aspects of NMA - Burr](https://onlinelibrary.wiley.com/doi/10.1155/2013/961360)
* [Comparison of joint page's test on SITMUF to MUF and CUMUF - Jones](https://esarda.jrc.ec.europa.eu/publications/esarda-bulletin-n15_en)