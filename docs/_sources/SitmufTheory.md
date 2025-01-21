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

The covariance matrix itself is often calculated using relative standard deviations, similar to the calculation for $\sigma$muf. In fact, the diagonal terms (i.e., $\Sigma_{1,1},  \Sigma_{2,2}, ... $) are the variance of the material balance (the covariance of material balance $i$ with itself is the variance). Recall the expression that was derived from $\sigma$muf. 

$$
        \sigma_{i,i}^2 & \approx 
    \sum_{l \in l_0} \left( \left(\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i}I_{l,t}\right)^2 * ((\delta_{R,l})^2 + (\delta_{S,l})^2) \right) 
    + \sum_{l \in l_2} \left( (C_{i,l})^2 * ((\delta_{R,l})^2 + (\delta_{S,l})^2) \right) \\
    & + \sum_{l \in l_2} \left( (C_{i-1,l})^2 * ((\delta_{R,l})^2 +  (\delta_{S,l})^2)  \right) \\
    &  + \sum_{l \in l_1} \left( \left( \int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i} O_{l,t} \right)^2 * ((\delta_{R,l})^2 + (\delta_{S,l})^2) \right)
$$

:::{note}
The covariance term for the variance **will** be included in the covariance matrix calculation.
:::

The off-diagonal is calculated in a similar manner, but has more terms. The off-diagonal is the covariance between material balance $i$ and $j$.

$$
    \sigma_{i,j}^2  \approx
    \text{cov} \bigg(& \sum_{l \in l_0}\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i}I_{t,l} - \sum_{l \in l_1}\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i}O_{t,l} -  \sum_{l \in l_2}(C_{i,l} - C_{i-1, l}), \\
    & \sum_{l \in l_0}\int_{t=\text{MBP}_{j-1}}^{\text{MBP}_j}I_{t,l} - \sum_{l \in l_1}\int_{t=\text{MBP}_{j-1}}^{\text{MBP}_j}O_{t,l} -  \sum_{l \in l_2}(C_{j,l} - C_{j-1, l}) \bigg)\\
$$

Following the same rules used to derive $\sigma$muf leads to the expression for the covariance off diagonal:

$$
\sigma_{i,j}^2  \approx
    & \sum_{l \in l_2} \left( \left(   C_{i,l}C_{j,l} + C_{i-1,l}C_{j-1,l}   \right) * (\delta_{S,l})^2 \right) \\
     - & \sum_{l \in l_2} \left( \left(   C_{i,l}C_{j-1,l}    \right) * \left(  (\delta_{S,l})^2 + P(j-1 == i)*(\delta_{R,l})^2 \right)   \right)\\
     - & \sum_{l \in l_2} \left( \left(   C_{i-1,l}C_{j,l}    \right) * \left(  (\delta_{S,l})^2 + P(i-1 == j)*(\delta_{R,l})^2 \right)   \right)\\
     + &  \sum_{l \in l_0} \left( \left(\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_j}I_{t,l}\right) \left( \int_{t=\text{MBP}_{j-1}}^{\text{MBP}_j}I_{t,l} \right)  (\delta_{S,l})^2 \right) \\
     + & \sum_{l \in l_1} \left( \left(\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_j}O_{t,l}\right) \left( \int_{t=\text{MBP}_{j-1}}^{\text{MBP}_j}O_{t,l} \right)  (\delta_{S,l})^2 \right) \\
$$

Where 

$$

    [P] \equiv 
    \begin{cases}
      0 & P \text{ is false} \\
      1 &  P \text{ is true} \\ 
    \end{cases}

$$

:::{note}
The goal of the SITMUF transform is to result in an standardized independent 
::: 

## Discussion

The Cholesky-based approach above has the property that the variance of SITMUF decreases with time as the estimated covariance matrix approaches the true value. This is the implementation used in MAPIT, however, one could also do a yearly SITMUF transform wherein the transform was applied only after the covariance matrix was well approximated from a year's worth of material balances. 

## Implementation
:::{important}
Note that this function is not intended to be used standalone through direct calls, rather, it is designed to be called through the `MBArea` class of `StatsProcessor`. 
:::

The SITMUF implementation in MAPIT is particularly computationally intensive as the "NRTA" type calculation is used. In a simulation space, we can calculate the entire covariance matrix at once with all entries from all balance periods. However, a "NRTA" styled calculation performs the SITMUF transform with a reduced covariance matrix that grows as new observations are added. This results in a decrease in variance of SITMUF over time. 

The covariance matrix is a $NxN$ matrix at the N-th material balance period. Since MAPIT adopts the "NRTA" style calculation, all $NxN$ entries must be updated at each balance period which simulates the arrival of new information. The MAPIT SITMUF calculation is not well vectorized as the $NxN$ must be resized and calculated at each balance. The calculation starts by looping over balance periods and each entry in the covariance matrix at balance $P$:


```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 691-692
:language: python
:linenos:
:lineno-start: 691
```

The variables for the different times have a different meaning than in the expressions that were defined above. This is for legacy purposes and to improve alignment with the papers. The following table describes the mapping between the derived expressions and associated code:

| Model Component | Code Expression |
| --- | --- |
| Balance $i$ | `I` |
| Balance $j$ | `IPrime`

For simplicity, the diagonal and off-diagonal terms are broken into multiple components.

### Diagonal terms

```{math}
:class: only-dark
    \sigma_{i,i}^2 & \approx 
    \colorbox{#5755aa}{$\sum_{l \in l_0} \left( \left(\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i}I_{l,t}\right)^2 * ((\delta_{R,l})^2 + (\delta_{S,l})^2) \right) $}
    + \colorbox{#A2782A}{$\sum_{l \in l_2} \left( (C_{i,l})^2 * ((\delta_{R,l})^2 + (\delta_{S,l})^2) \right)$} \\
    & +  \colorbox{#3E8E87}{$\sum_{l \in l_2} \left( (C_{i-1,l})^2 * ((\delta_{R,l})^2 +  (\delta_{S,l})^2)  \right)$}
     -  \colorbox{#CC3300}{$\sum_{l \in l_2} \left( 2C_{i-1,l}C_{i,l}(\delta_{S,l})^2  \right)$} \\
    &  +  \colorbox{#0074CC}{$\sum_{l \in l_1} \left( \left( \int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i} O_{l,t} \right)^2 * ((\delta_{R,l})^2 + (\delta_{S,l})^2) \right)$}
```

<span style="color:#5755aa; font-weight:bold">Term 1</span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 728-731
:language: python
:linenos:
:emphasize-lines: 4
:lineno-start: 728
```

<span style="color:#A2782A; font-weight:bold">Term 2</span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 742-748
:language: python
:linenos:
:emphasize-lines: 7
:lineno-start: 748
```

<span style="color:#3E8E87; font-weight:bold">Term 3</span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 742-759
:language: python
:linenos:
:emphasize-lines: 16
:lineno-start: 742
```

<span style="color:#CC3300; font-weight:bold">Term 4</span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 742-759
:language: python
:linenos:
:emphasize-lines: 17
:lineno-start: 742
:caption: The factor 2 is included later when the terms are added and assigned to the covariance matrix.
```

<span style="color:#0074CC; font-weight:bold">Term 5</span>

```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 734-739
:language: python
:linenos:
:lineno-start: 739
:emphasize-lines: 6
```

### Off-diagonal terms

```{math}
:class: only-dark

\sigma_{i,j}^2  \approx
    &  \colorbox{#5755aa}{$\sum_{l \in l_2} \left( \left(   C_{i,l}C_{j,l} + C_{i-1,l}C_{j-1,l}   \right) * (\delta_{S,l})^2 \right)$} \\
     - & \colorbox{#A2782A}{$\sum_{l \in l_2} \left( \left(   C_{i,l}C_{j-1,l}    \right) * \left(  (\delta_{S,l})^2 + P(j-1 == i)*(\delta_{R,l})^2 \right)   \right) $}\\
     - &  \colorbox{#3E8E87}{$\sum_{l \in l_2} \left( \left(   C_{i-1,l}C_{j,l}    \right) * \left(  (\delta_{S,l})^2 + P(i-1 == j)*(\delta_{R,l})^2 \right)   \right) $}\\
     + &   \colorbox{#CC3300}{$ \sum_{l \in l_0} \left( \left(\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_j}I_{t,l}\right) \left( \int_{t=\text{MBP}_{j-1}}^{\text{MBP}_j}I_{t,l} \right)  (\delta_{S,l})^2 \right)  $}\\
     + &  \colorbox{#0074CC}{$ \sum_{l \in l_1} \left( \left(\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_j}O_{t,l}\right) \left( \int_{t=\text{MBP}_{j-1}}^{\text{MBP}_j}O_{t,l} \right)  (\delta_{S,l})^2 \right) $} \\
```

<span style="color:#5755aa; font-weight:bold">Term 1</span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 808-818
:language: python
:linenos:
:emphasize-lines: 8,9,10
:lineno-start: 808
```

<span style="color:#A2782A; font-weight:bold">Term 2</span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 808-828
:language: python
:linenos:
:emphasize-lines: 13-18
:lineno-start: 808
```

<span style="color:#3E8E87; font-weight:bold">Term 3</span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 808-838
:language: python
:linenos:
:emphasize-lines: 23,24,26,27,28,29
:lineno-start: 808
```

<span style="color:#CC3300; font-weight:bold">Term 4</span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 787-794
:language: python
:linenos:
:emphasize-lines: 5,6,7
:lineno-start: 787
```

<span style="color:#0074CC; font-weight:bold">Term 5</span>

```{literalinclude} ../../MAPIT/core/StatsTests.py
:lines: 797-805
:language: python
:linenos:
:lineno-start: 797
:emphasize-lines: 6,7,8
```

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