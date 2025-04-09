# SITMUF

## Historical context 
The statistical properties of the MUF sequence has been studied extensively, and as early as the 1980s, it was noted that there was correlation between successive material balance periods. Pike and Woods were the first to develop a concept called ITMUF (Independent Transformed MUF) and later SITMUF (Standardized Independent MUF). The SITMUF sequence is a transformed material balance sequence wherein the mean is approximately zero and the standard deviation is approximately one. There are two key advantages to performing statistical testing on such an independent sequence:

* Alarm thresholds for SITMUF depend only on the sequence length, not the form or properties of the MUF covariance 
    * This alleviates the need to determine alarm thresholds by strictly using simulation
* In a near-real time accountancy context, the variance of SITMUF decreases as the approximate covariance of the MUF sequence approaches the true value
    * Consequently, the detection probability of SITMUF increases over time, often resulting in a higher detection probability than the MUF sequence alone

The transformation from MUF to SITMUF was quite difficult until Picard showed that the SITMUF transform can be easily expressed using the [Cholesky decomposition](https://en.wikipedia.org/wiki/Cholesky_decomposition). A series of papers in the late 1980s onward showed that applying Page's trend test to SITMUF performs well for a wide range of potential material loss scenarios when the pattern is not known. Page's trend test on SITMUF has been frequently used as an effective test in nuclear material accountancy.

## Theory

Recall that the **muf** sequence is defined as follows:

$$
     \boldsymbol{\text{muf}} = \{ \text{muf}_0, \text{muf}_1, ... \text{muf}_n \}
$$

With 

$$
\text{muf}_i =  \sum_{l \in l_0}\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i}I_{t,l} - \sum_{l \in l_1}\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i}O_{t,l} -  \sum_{l \in l_2}(C_{i,l} - C_{i-1, l})
$$

It's generally assumed that since the error models are normally distributed, individual muf values (i.e., mbp$_i$) and the muf sequence (i.e., **muf**) will also be normally distributed. Consequently, the muf sequence can be thought of as a multivariate normal distribution such that:

$$
    \boldsymbol{\text{muf}} \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})
$$

The covariance matrix contains the covariance between different material balances in the sequence. For example, consider the entry $\sigma_{2n}^2$ of the covariance matrix below. This term is the variance between material balance $n$ and $2$.

$$
\begin{aligned}
 \boldsymbol{\Sigma} & = \begin{pmatrix}
  {\sigma}_{11}^2 & {\sigma}_{12}^2 & \ldots & {\sigma}_{1n}^2 \\
  {\sigma}_{21}^2 & {\sigma}_{22}^2 & \ldots & {\sigma}_{2n}^2 \\
  \vdots          & \vdots          & \ddots & \vdots          \\
  {\sigma}_{n1}^2 & {\sigma}_{n2}^2 & \ldots & {\sigma}_{nn}^2 \\
 \end{pmatrix}
  =  \begin{pmatrix}
  \boldsymbol{\Sigma_{i-1}} & \boldsymbol{\sigma_{i-1}} \\
  \boldsymbol{\sigma_{i-1}}^T & \sigma_{i,i} \\
 \end{pmatrix}
\end{aligned}
$$(eqn:cov)

:::{note}
The covariance matrix $\boldsymbol{\Sigma}$ is symmetric (i.e., $\sigma_{1,2} = \sigma_{2,1}$). 
:::

The SITMUF statistic is muf with a mean of zero and standard deviation of one. This can be initially considered through the subtraction of the sequence mean and division by the sequence standard deviation. The independent material balance sequence can be expressed by estimating the sequence mean through the conditional expectation given all previously observed muf values:

$$
    \text{itmuf}_i = \text{muf}_i -  E(\text{muf}_i  | \text{muf}_{i-1}, \text{muf}_{i-2}, ..., \text{muf}_{0})
$$

Then note that SITMUF is ITMUF divided by the standard deviation:

$$
    \text{sitmuf}_i = \text{itmuf}_i / \sigma_{\text{itmuf}} \\
$$

The using the expression for conditional expectation of the [multivariate normal distribution](https://en.wikipedia.org/wiki/Multivariate_normal_distribution) with the covariance expression {eq}`eqn:cov` from the expression then becomes:

$$
    \text{itmuf}_i = \left( \text{muf}_i -   \boldsymbol{\sigma_{i-1}}^T \boldsymbol{\Sigma_{i-1}}^{-1} \text{muf}_{i-1}  \right)  \\
    \sigma_{\text{itmuf}} = \sigma_{i,i} - \boldsymbol{\sigma_{i-1}}^T \boldsymbol{\Sigma_{i-1}}^{-1} \boldsymbol{\sigma_{i-1}}
$$

[Picard](https://digital.library.unt.edu/ark:/67531/metadc1086101/m2/1/high_res_d/5557057.pdf) showed a convenient way to calculating the above expression is through the use of the Cholesky decomposition. Since Picard fully derives the relationship between the expression above and the Cholesky decomposition, we refrain from showing that work here. The final expression for SITMUF becomes

$$
    \boldsymbol{\Sigma}_i = \boldsymbol{\text{C}_i}\boldsymbol{\text{C}_i}^T \\
    \text{sitmuf}_i = \boldsymbol{\text{C}_i}^{-1} \text{muf}_{i} \\
$$

Where $ \boldsymbol{\text{C}_i}$ is the lower triangular Cholesky factor of the covariance matrix.

### Calculation of the covariance matrix

The covariance matrix is calculated using the `AuxFunctions.calcCovMat()` function. Setting up and calculating the covariance matrix is the most tedious and involved part of the SITMUF transform and is handled by it's own function. More details regarding the covariance matrix can be found [here](./covmat.md).  

## Discussion

It's important to note that the variance of SITMUF decreases with time as the estimated covariance matrix approaches the true value. The SITMUF transform is a ''forward-only'' method in that the transformed MUF values only benefit from the current covariance matrix entries. So, for example, even if you have an entire MUF sequence, the first MUF (MUF$_1$) value can't benefit from the fact that you have an entire covariance matrix filled with entries from the entire sequence. It only benefits from the information contained in the 1x1 submatrix of the covariance matrix (similarly MUF$_4$ only benefits from the 4x4 submatrix of the covariance matrix) There's no way to ''back-propagate'' the covariance matrix to previous MUF values, and this is be design. SITMUF values are usually fixed from a regulatory perspective. It's not desirable to  back correct SITMUF in most cases. If there was ever a use case to ''back-propagate'' the covariance matrix to past values, a different model would be required (perhaps something like a Kalman filter which could estimate state).



## Implementation

The SITMUF implementation in MAPIT isn't very expensive thanks to optimized linear algebra libraries used to perform the Cholesky decomposition and other associated matrix operations.  The SITMUF function only computes this quantity:

$$
    \boldsymbol{\Sigma}_i = \boldsymbol{\text{C}_i}\boldsymbol{\text{C}_i}^T \\
    \text{sitmuf}_i = \boldsymbol{\text{C}_i}^{-1} \text{muf}_{i} \\
$$


Each SITMUF realization (that is, each iteration) is calculated separately as the Cholesky decomposition from Numpy isn't vectorized (it's pretty quick on modern machines, anyways). We start by converting the MUF values from a continuous vector in time to a discrete vector on a per balance basis:

<span style="font-size: 1.5em; font-weight: bold;"><code>StatsTests.py</code></span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:start-after: _sitmuf_IDs-start
:end-before: _sitmuf_IDs-end
:language: python
:linenos:
:lineno-match:
```
After that, we attempt to perform the Cholesky decomposition. The decomposition will fail if the covariance matrix wasn't constructed properly, so we try to pass a warning/error if this happens.

<span style="font-size: 1.5em; font-weight: bold;"><code>StatsTests.py</code></span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:start-after: _sitmuf_chol-start
:end-before: _sitmuf_chol-end
:language: python
:linenos:
:lineno-match:
```

If the decomposition succeeds, then we proceed directly to the transform itself:

<span style="font-size: 1.5em; font-weight: bold;"><code>StatsTests.py</code></span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:start-after: _sitmuf_transform-start
:end-before: _sitmuf_transform-end
:language: python
:linenos:
:lineno-match:
```

:::{important}
MAPIT's implementation calculates the entire SITMUF sequence in one pass resulting in the full length sequence. In practice, a more near-real time approach is adopted wherein, at each balance period, new values are appended to the covariance matrix and the MUF sequence is extended. Then the calculation is performed on the new sequence and the last value of the resulting SITMUF sequence is the current SITMUF value that is recorded for regulatory purposes. There's no benefit for us to perform the calculation this way as the values are the same if you iteratively calculate SITMUF (with a increasingly large covariance matrix) or do it at once as we do. 
:::

We then convert the discrete SITMUF sequence to a continuous representation before continuing through all iterations. Then the final matrix is returned.


## Further reading
* [Speed and Culpin](https://www.jstor.org/stable/2981719)
* [Avenhaus and Jaech](https://resources.inmm.org/jnmm/subdividing-material-balances-time-andor-space)
* [Handbook of Nuclear Engineering: Proliferation Resistance and Safeguards](https://link.springer.com/referenceworkentry/10.1007/978-0-387-98149-9_29#Sec1_29)
* [Picard](https://digital.library.unt.edu/ark:/67531/metadc1086101/m2/1/high_res_d/5557057.pdf)
* [Revisiting statistical aspects of NMA - Burr](https://onlinelibrary.wiley.com/doi/10.1155/2013/961360)
* [Fundamentals of materials accounting for nuclear safeguards](https://inis.iaea.org/collection/NCLCollectionStore/_Public/21/068/21068554.pdf)

* [Jones 1](https://inis.iaea.org/search/search.aspx?orig_q=RN:18086541)
    * Pages 402-408
* [Jones 2](https://esarda.jrc.ec.europa.eu/publications/esarda-bulletin-n7_en)
    * Pages 19-22