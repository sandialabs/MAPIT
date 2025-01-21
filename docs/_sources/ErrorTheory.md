# Error model

---

## Historical context
The multiplicative error model used in MAPIT was chosen based on the widespread and commonplace use within the IAEA. It was recognized that as early as the IAEA's founding in 1957 that there would be a need to account for nuclear material in facilities. This created the subsequent need for statistical methods to estimate uncertainties in measurements. One key component for the selection of an error model is the necessity to propagate error from many measurements for downstream statistical analyses. The multiplicative error model arose from the need to propagate measurements and perform top-down (i.e., empirical) uncertainty quantification using both in-field IAEA measurements and operator declared measurements. The specific values used in the multiplicative error models are determined using a variety of techniques that changes based on the context of the underlying data. We refer the reader to [supplementary reading section](#further-reading) for more information on the history and determination of the multiplicative error model.

## Theory

No measurement, except counting, is completely accurate which results in a non-zero measurement error. This is the reason that robust statistical analysis of the material balance is required; if material in a facility were exactly known, detecting loss of that material would be trivial. Statistical analyses in material accountancy often assumes a multiplicative error model (describe in the following equation)

$$
    \widetilde{x}_t = x_t (1 + r_t + s_t)
$$

Where:
* $\widetilde{x}_t$ is the observed value (i.e., what is actually measured) at time $t$
* $x$ is the true, but unknowable value at time $t$
* $r_t$ is relative random error of $x$
    * Specifically $r_t$ is a random variate of the distribution $\mathcal{N}(0, \delta_r^2)$ where $\delta_r^2$ is the random relative standard deviation.
* $s_t$ is the relative systematic error of $x$
    * Specifically, $s_t$ is a random variate of the distribution $\mathcal{N}(0, \delta_s^2)$ where $\delta_s^2$ is the systematic relative standard deviation.

Here, random error refers to sources of error that can be reduced through repeated measurements of the same item. Systematic errors refers to short-term biases that are generally irreducible. These systematic biases can arise from a variety of sources such as calibration errors. Regardless of the measurement type, errors are characterized by a mean zero normal distribution with non-zero standard deviation. The distributions characterizing the random and systematic error can vary based on a variety of factors such as measurement type, measurement system, and even the specific isotope measured. 

:::{tip}
Systematic errors behave as a bias. Consequently, the systematic variate, $S_t$, applied to the true value $x_t$, from the multiplicative model described above is not updated at every timestep. This contrasts with the random variate which _is_ updated at each time step. The systematic variate is held constant and only updated on a periodic basis that corresponds to a specified calibration period. The specifics of the calibration period are measurement system specific.
:::

:::{important}
As of version 1.4.6, there is no functionality to specify a calibration period directly. The API can be combined with data manipulation to simulate different calibrations by slicing the data and passing it to `MAPIT.core.Preprocessing.SimErrors`. 

**By default, MAPIT assumes a single calibration for the length of the dataset that does not vary with time.** For example, a time series with 1000 steps will be assumed to have a single systematic variate, drawn from a distribution described by the user supplied error matrix, that is applied to every time step and does not change with time. A new feature is planned for FY25 that will add the capability to specify a calibration period.
:::






## Implementation
:::{important}
Note that this function is not intended to be used standalone through direct calls, rather, it is designed to be called through the `MBArea` class of `StatsProcessor`. 
:::


The multiplicative error model described in the introduction assumes that there is a single iteration and location. For example, the model in the introduction might express the simulated error for a single input key measurement point. There might be multiple key measurement points in practice resulting an error model with location $p$ and time $t$ such that:

$$
    \widetilde{x}_{p,t} = x_{p,t} (1 + r_{p,t} + s_{p,t})
$$

It is often desireable to consider simulated statistics and calculate error for multiple iterations to help determine performance statistics of a safeguards system even if, in practice, only a single iteration is measured. The multiplicative error model can be further expanded such that an iterative dimension, $n$, that reflects independent draws of the underlying random and systematic error distributions, is also considered. Note that there is no iteration added to the unobservable true value, $x_{p,t}$ as it is not a random variate. 

$$
    \widetilde{x}_{n,p,t} = x_{p,t} (1 + r_{n,p,t} + s_{n,p,t})
$$

For simplicity, assume that the systematic error does not have a calibration period and applies for an entire iteration (i.e., the same bias is applied for all time steps of an iteration). One naive implementation of the multiplicative model might then be as follows:

```python
for n in range(len(iterations)):
    for p in range(len(locations)):
        sysError = np.random.normal(loc = 0, scale = sysSTD)

        for t in range(len(timesteps)):
            randomError = np.random.normal(loc = 0, scale = randSTD)
            x_observed[n, p, t] = x_true[p, t] * (1 + randomError + sysError)

```

This approach is valid, but scales poorly. MAPIT vectorizes both the iteration and timestep dimension on a per location basis. Each location might have a different sample rate, so it is not possible to develop a fully vectorized implementation. The multiplicative model, in a vectorized form, can first be expressed as follows when vectorizing the time dimensions:

$$
    \widetilde{\boldsymbol{x}}_\boldsymbol{n,p} = \boldsymbol{x}_{p} (1 + \boldsymbol{r}_{n,p} + \boldsymbol{s}_{n,p})
$$

Additionally, the iterative dimension can be vectorized resulting in the following:

$$
    \widetilde{\boldsymbol{X}}_\boldsymbol{p} = \boldsymbol{x}_{p} (1 + \boldsymbol{R}_{p} + \boldsymbol{S}_{p})
$$

:::{Note}
While the random error component, $R_{n,p,t}$ is sampled at every time step, sensor setup might complicated the specification of the systematic error component. It is assumed here that the systematic error changes with location but _not_ time as no calibration time is assumed ($S_{n,p,t=0} = S_{n,p,t=50} = S_{n,p,t=t}$).
:::

The implementation of this error model is performed in MAPIT by `MAPIT.core.Preprocessing.SimErrors` starting on line 352: 

```{literalinclude} ../../MAPIT/core/Preprocessing.py
:lines: 352-352
:language: python
```

The function generates `iterations` simulated realizations of measurements (i.e., the iteration dimension $n$) for each list entry. Each `iteration` represents a possible result of measuring at the specific key measurement point (i.e., location dimension $p$) represented by the list entry.

First, a list of arrays is initialized to hold the errors calculated by the function (Lines 408-409). 

```{literalinclude} ../../MAPIT/core/Preprocessing.py
:lines: 408-409
:language: python
:linenos:
:lineno-start: 408
```

Each entry in the `AppliedError` list is an array with shape (iterations $n$, time steps $t$) and _presumably_ refers to a different location in a measurement type. For example, the first entry in the list might be a (time steps $t$, 1) shaped array of data collected at the first input key measurement point. Since each list entry might have a different number of time steps, the arrays are stored in a list rather than being concatenated. The list and constituent arrays are preinitalized.

The main calculation loop occurs between lines 442 and 479:

```{literalinclude} ../../MAPIT/core/Preprocessing.py
:lines: 442-479
:language: python
:linenos:
:lineno-start: 442
```




`SimErrors` has a parameter `batchSize` that controls the number of `iterations` that are calculated at once. The most efficient implementation would calculate all `iterations` at once using a single matrix calculation. However, this could consume more memory than available in some scenarios, so the `batchSize` parameter is provided. The code tries to batch `iterations` into `batchSize` chunks. If `iterations` is not equally divisible by `batchSize`, then an extra `remRuns` sized calculation is performed after the all `iterations/batchSize` chunks are calculated.

<!-- For each batch, the multiplicative error model is calculated and applied. The table below shows the components of the model and the equivalent code. The [`reshape`](https://numpy.org/doc/stable/reference/generated/numpy.reshape.html) method has been omitted from the table for improved clarity.  -->


MAPIT specifically uses vectorized representations to more efficiently calculated the simulated error model. The sections below map the model components to the relevant code expressions. 

| Model Component | Code Expression |
| --- | --- |
| $\boldsymbol{r}_{n=1:\textrm{batch},p} $ | `randRSD = np.random.normal(size=(batchSize, rawData[i].shape[0], 1), loc=0, scale=ErrorMatrix[i,0])`{l=python}|
| $\boldsymbol{s}_{n=1:\textrm{batch},p} $ | `sysRSD = np.random.normal(size=(batchSize, 1, 1), loc=0, scale=ErrorMatrix[i,1])`{l=python} |
| $\boldsymbol{x}_{p}$ | `rawData`{l=python} |
|  $\widetilde{\boldsymbol{x}}_{n=1:\textrm{batch},p}$ | `AppliedError[i][startIdx:endIdx,] = rawData[i][:,0].reshape((1,-1)) * (1+sysRSD+randRSD).reshape((batchSize,-1))`{l=python} |

:::{important}
Note that `sysRSD` has a shape of 1 for dim 1 (i.e., `sysRSD.shape[1] = 1`{l=python}) as a single random variate from the underlying distribution is applied to _all_ time steps for location `i`. [Numpy broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) ensures that the shape of $\boldsymbol{S_{n,p}}$ is the same for all $t$. This will be configurable in a future update.
:::

Additional code present in this section is used to support GUI changes, such as updating of a progress bar update, and is not important to the core multiplicative error model calculation.


## Further reading
* [Statistical error model-based and GUM-based analysis of measurement uncertainties in nuclear safeguards - a reconciliation](https://esarda.jrc.ec.europa.eu/publications/statistical-error-model-based-and-gum-based-analysis-measurement-uncertainties-nuclear-safeguards_en)
    * Discussion about the development of the multiplicative error model and how UQ models like GUM relate
* [International Target Values for Measurement Uncertainties in Safeguarding Nuclear Materials](https://nucleus.iaea.org/sites/connect/ITVpublic/Resources/International%20Target%20Values%20for%20Measurement%20Uncertainties%20in%20Safeguarding%20Nuclear%20Materials.pdf)
    * Reference values for $\delta_r$ and $\delta_s$ for different measurement systems and materials
* Near Real Time Accountancy (IAEA STR-403)
    * Finalized but not yet released by IAEA at time of writing
* [Handbook of Nuclear Engineering: Proliferation Resistance and Safeguards](https://link.springer.com/referenceworkentry/10.1007/978-0-387-98149-9_29#Sec1_29)
    * Specifically the section on "Statistics for Accountancy"