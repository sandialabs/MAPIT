# GEMUF

## Historical Context
There have been various schemes for analyzing the material balance sequence (i.e., MUF). The SITMUF approach attempts to develop a sequence of _residuals_ wherein the MUF sequence is converted to a standardized sequence and monitored for trend changes.

In contrast, GEMUF (geschatzter, or estimated, MUF) attempts instead to develop a distance-based metric to detect anomalies. However, GEMUF is very sensitive to misspecified covariance matrices.

## Theory
Recall that the **muf** sequence is defined as follows:

$$
     \boldsymbol{\text{muf}} = \{ \text{muf}_0, \text{muf}_1, ... \text{muf}_n \}
$$

With 

$$
\text{muf}_i =  \sum_{l \in l_0}\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i}I_{t,l} - \sum_{l \in l_1}\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i}O_{t,l} -  \sum_{l \in l_2}(C_{i,l} - C_{i-1, l})
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

The simplest statistical test to detect a loss would be to simply test two hypotheses:

$$

\begin{aligned}
& H_0 :  E(\boldsymbol{\text{muf}}_i) = 0 \text{ for } i \in \{1,2,...,N\} \\
& H_1 :  E(\boldsymbol{\text{muf}}_i) = M_i \text{ for }  i \in \{1,2,...,N\} \\
& \text{where} \\
& \sum M_i  =  M > 0 \\
\end{aligned}

$$

For all loss patterns, $\textbf{M}_N^T = \{M_1, M_2, ... M_N\}$, where $M_i$ is the loss in period $i$, the optimal test to compare $H_0$ and $H_1$ is a Neyman-Pearson test. Siefert showed the test statistic can be defined as:

$$

Z = \boldsymbol{M}_N^T {\Sigma}_N^{-1} \textbf{muf}_N

$$

With the test formulated as:

$$

Z
\begin{cases}
> \text{k}_\alpha: \text{ reject } H_0  \\
\leq \text{k}_\alpha: \text{ reject } H_1  \\
\end{cases}

$$

There's two challenges with this test. First, the test doesn't provide sequential decisions (not necessarily a problem considering the test can still be calculated sequentially, which we will do). This can be remedied by simply calculating the test statistic for each period and making decisions as such:

$$

{ZG}_i= \boldsymbol{M}_i^T {\Sigma}_N^{-1} \textbf{muf}_i

$$

with decision process:

$$
{ZG}_i
\begin{cases}
>s(i): \text{ reject } H_0  \\
\leq s(i): \text{ no decision }   \\
\end{cases}
$$

and for the final period:

$$
{ZG}_N
\begin{cases}
>s(N): \text{ reject } H_0  \\
\leq s(N): \text{ no reject } H_1  \\
\end{cases}
$$

:::note
Here all interim test statistic calculations are required to be below a threshold for $H_0$ to be rejected.
:::

 Second, and more problematic, is the requirement that the loss pattern, $M_N$ is known. It is reasonable to approximate $\boldsymbol{M_N}$ as $\boldsymbol{M_N} \approx \textbf{muf}_N$ such that $\boldsymbol{\hat{M_N}} = \textbf{muf}_N$ by considering that $E(\boldsymbol{\text{muf}}_i) = M_i$. 

The test statistic then becomes 

$$

\begin{aligned}
    Z & = {\left(\hat{\boldsymbol{M}_N}\right)}^T {\Sigma}_N^{-1} \textbf{muf}_N \\
    & = {\textbf{muf}_N}^T {\Sigma}_N^{-1} \textbf{muf}_N
\\
\end{aligned}

$$

:::note
The details behind the covariance calculation can be found in [sitmuf theory](./SitmufTheory.md)
:::


Siefert noted that using a single MUF value at each step (i.e.,  M_i$) can lead to significant variance. It was proposed to use a weighted value such that:

$$

M_i = \frac{1}{7} \left( \text{muf}_{i-2} +  \text{muf}_{i-1} + 3 \text{muf}_i +  \text{muf}_{i+1} +  \text{muf}_{i+2} \right)

$$

This approach has lower variance, but is no longer unbiased. In MAPIT we implement both approaches, the use of the single MUF value is V1 and the use of the weighted values is V5B3, following the notation in the original paper.


## GEMUF implementation
Since both GEMUF and SITMUF both require calculation of the covariance matrix, this is only done once and then used for any requested SITMUF or GEMUF calculations. Details of the covariance matrix calculation can be found in the SITMUF section and won't be repeated here.

:::seealso
[Covariance Matrix](./covmat.md)
:::

The GEMUF functions are responsible for calculating the GEMUF sequence (either V1 or V5B3), effectively performing the calculation below as it's assumed the covariance matrix has already been calculated:

$$

\begin{aligned}
    Z & = {\left(\hat{\boldsymbol{M}_N}\right)}^T {\Sigma}_N^{-1} \textbf{muf}_N \\
    & = {\textbf{muf}_N}^T {\Sigma}_N^{-1} \textbf{muf}_N
\\
\end{aligned}

$$

Unlike the SITMUF sequence, GEMUF is calculated sequentially for each balance period. That is, for a given MUF sequence, only a single test statistic is produced. Therefore, we have to loop over the entire MUF sequence:

<span style="font-size: 1.5em; font-weight: bold;"><code>StatsTests.py</code></span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:start-after: _GEMUF_V1-start
:end-before: _GEMUF_V1-end
:language: python
:linenos:
:lineno-match:
```

We generate per-balance test statistics for GEMUF by considering subsections of the original sequence with increasing covariance matrix size:

<span style="font-size: 1.5em; font-weight: bold;"><code>StatsTests.py</code></span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:start-after: _GEMUF_V1-start
:end-before: _GEMUF_V1-end
:language: python
:linenos:
:lineno-match:
:emphasize-lines: 3,4
```

For GEMUF-V1, the test statistic is straightforward to calculate:

<span style="font-size: 1.5em; font-weight: bold;"><code>StatsTests.py</code></span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:start-after: _GEMUF_V1-start
:end-before: _GEMUF_V1-end
:language: python
:linenos:
:lineno-match:
:emphasize-lines: 5
```

Following the calculation of GEMUF-V1, the discrete sequence of GEMUF-V1 values are converted to a continuous time series.

The GEMUF-V5B3 calculation differs slightly from the GEMUF-V1 calculation. The GEMUF-V5B3 still iterates over the material balance periods, but a MUF ''window'' is created that corresponds to values needed in the weighting. Note the creation of the MUF window, generated from the continuous MUF values. The creation of this window is only valid when 5 consecutive MUF values are available:

<span style="font-size: 1.5em; font-weight: bold;"><code>StatsTests.py</code></span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:start-after: _GEMUF_V5B3Window-start
:end-before:  _GEMUF_V5B3Window-end
:language: python
:linenos:
:lineno-match:
```

If there's a valid window, then the GEMUF-V5B3 is calculated. It's important to note that we store the calculated weighted MUF values as the GEMUF-V5B3 calculation requires a _sequence_ of values, not just the instantaneous value (in the code, `MSSeq` holds the weighted MUF values).


<span style="font-size: 1.5em; font-weight: bold;"><code>StatsTests.py</code></span>
```{literalinclude} ../../MAPIT/core/StatsTests.py
:start-after: _GEMUF_V5B3C-start
:end-before:  _GEMUF_V5B3C-end
:language: python
:linenos:
:lineno-match:
```

After calculating the the discrete GEMUF-V5B3 sequence, it is converted to a continuous time series before being returned.

:::{important}
The GEMUF-V5B3 test isn't valid for the first and last two material balance periods because it requires a weighted average that includes the two previous and future balances. Seifert's original paper didn't describe what to do with the test on the tails of the balance sequence, so we choose to represent those values as `np.nan`. It's important to note this as sometimes plotting libraries will drop those values when plotting. For example, matplotlib will often drop `np.nan` values resulting in a plotted sequence that appears to be missing the first two and last two sequence intervals.
:::



## Further reading
* [The GEMUF Test (Seifert)](https://inis.iaea.org/records/jfm5m-x8s14)
    * Note this is 675 pages long as the original GEMUF test paper is part of the IAEA symposium collection from 1986.