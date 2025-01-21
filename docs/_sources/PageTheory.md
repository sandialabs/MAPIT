# Page's trend test

## Historical context
The statistical discussed so far (MUF, $\sigma$MUF, and SITMUF) are insufficient alone to detect a loss of material. Statistical testing must be performed. For example, the [CuMUF](CumufTheory.md) test is a simple one that compares the summed MUF values to a threshold. There are many different statistical tests that have been studied and deployed for use in material accountancy. One such test is Page's trend test. Page has been a popular sequential test given its relatively good performance on a wide range of loss scenarios. Page's trend test can be applied to any sequence, but is most commonly applied to SITMUF. Page's trend test on SITMUF specifically is what is implemented in MAPIT.



## Theory

Page's test is similar to CuMUF, but instead of allowing for negative values, the test statistic is constrained to positive values only. Page's statistic can be defined as:

$$
    P_i(\boldsymbol{y}) = \text{max}(P_{i-1}(\boldsymbol{y})+y_i-k,0)
$$

Where:
* $ P_i(\boldsymbol{y})$ is the $i$th page statistic for the sequence $\boldsymbol{y}$
* $P_{i-1}$ is the previous page statistic (zero if $i=0$)
* $y_i$ is the $i$th element of sequence $\boldsymbol{y}$
* $k$ is a hyper parameter

An alarm occurs if $P_i(\boldsymbol{y}) > h_i$ for some threshold $h_i$, although $h$ is often taken to be constant. Parameter $h$ is used to tune the false alarm probability while $k$ is designed to give some control over the size loss that the test is designed to detect. Generally, smaller $k$ is better for small protracted losses whereas larger $k$ is better for detecting abrupt losses. A good rule of thumb is to set $k=\sigma/2$ where $\sigma$ is the magnitude of the loss to detect in terms of material balance standard deviation. In practice, there might be two page's tests calculated on the same sequence, one for abrupt losses and one for protracted losses, each with a different set of $(h,k)$ values.  

## Implementation
:::{important}
Note that this function is not intended to be used standalone through direct calls, rather, it is designed to be called through the `MBArea` class of `StatsProcessor`. 
:::

:::{note}
As of MAPIT 1.4.6, `K` value is set to 0.5 and is only adjustable through the API, not the GUI.
:::

```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 914-925
:language: python
:linenos:
:lineno-start: 797
:caption: The implementation of the trend test is straightforward following the equation given in the theory section. The only addition from the page's equation above is the tiling in line 808 which copies the page test statistic for all time steps between material balances.
```

## Further reading
* [Jones 1](https://inis.iaea.org/search/search.aspx?orig_q=RN:18086541)
    * Pages 402-408
* [Jones 2](https://esarda.jrc.ec.europa.eu/publications/esarda-bulletin-n7_en)
    * Pages 19-22
* [Page's trend test](https://www.jstor.org/stable/2333009)