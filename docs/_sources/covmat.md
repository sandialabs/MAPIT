# Covariance Matrix

## Historical context

Generally, the covariance matrix is a matrix that describes the relationship between the elements of a multivariate normal distribution. The covariance matrix is a square matrix of size [n x n] where n is the number of elements in the multivariate normal distribution. The covariance matrix is a symmetric matrix and is defined as follows:

$$

\Sigma = \begin{bmatrix}
\sigma_{11} & \sigma_{12} & \sigma_{13} & \cdots & \sigma_{1n} \\
\sigma_{21} & \sigma_{22} & \sigma_{23} & \cdots & \sigma_{2n} \\
\sigma_{31} & \sigma_{32} & \sigma_{33} & \cdots & \sigma_{3n} \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
\sigma_{n1} & \sigma_{n2} & \sigma_{n3} & \cdots & \sigma_{nn}
\end{bmatrix}

$$

The covariance matrix for the material balance sequence is of particular importance for several statistical tests, including SITMUF and GEMUF. It's impossible to know the exact matrix in practice, but it can be estimated by knowing expected sensor performance. 


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
 \boldsymbol{\Sigma} & = \begin{bmatrix}
  {\sigma}_{11}^2 & {\sigma}_{12}^2 & \ldots & {\sigma}_{1n}^2 \\
  {\sigma}_{21}^2 & {\sigma}_{22}^2 & \ldots & {\sigma}_{2n}^2 \\
  \vdots          & \vdots          & \ddots & \vdots          \\
  {\sigma}_{n1}^2 & {\sigma}_{n2}^2 & \ldots & {\sigma}_{nn}^2 \\
 \end{bmatrix}
  =  \begin{bmatrix}
  \boldsymbol{\Sigma_{i-1}} & \boldsymbol{\sigma_{i-1}} \\
  \boldsymbol{\sigma_{i-1}}^T & \sigma_{i,i} \\
 \end{bmatrix}
\end{aligned}
$$(eqn:cov)


The covariance matrix itself is often calculated using relative standard deviations, similar to the calculation for $\sigma$muf. In fact, the diagonal terms (i.e., $\Sigma_{1,1},  \Sigma_{2,2}, ... $) are the variance of the material balance (the covariance of material balance $i$ with itself is the variance).  There's two key expressions; one for the covariance diagonals (i.e., $\sigma_{x,x}$) and one for the covariance off diagonals (i.e., $\sigma_{x,x^{\prime}}$). These are calculated by using various variance and covariance rules and propagating the terms.

Recall the expression that was derived from $\sigma$muf; which is used for the diagonals for the covariance matrix:

$$
    \sigma_{i,i}^2 & \approx 
    \sum_{l \in l_0} \left( \left(\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i}I_{l,t}\right)^2 * ((\delta_{R,l})^2 + (\delta_{S,l})^2) \right) 
    + \sum_{l \in l_2} \left( (C_{i,l})^2 * ((\delta_{R,l})^2 + (\delta_{S,l})^2) \right) \\
    & + \sum_{l \in l_2} \left( (C_{i-1,l})^2 * ((\delta_{R,l})^2 +  (\delta_{S,l})^2)  \right) \\
    &  + \sum_{l \in l_1} \left( \left( \int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i} O_{l,t} \right)^2 * ((\delta_{R,l})^2 + (\delta_{S,l})^2) \right)
$$


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

## Implementation

The covariance matrix is a $NxN$ matrix at the N-th material balance period. Since MAPIT adopts the "NRTA" style calculation, all $NxN$ entries must be updated at each balance period which simulates the arrival of new information. The MAPIT SITMUF calculation is not well vectorized as the $NxN$ must be resized and calculated at each balance. The calculation starts by looping over balance periods and each entry in the covariance matrix at balance $P$:

The covariance matrix is a $NxN$ matrix at the N-th material balance period. Since MAPIT adopts the "NRTA" style calculation, all $NxN$ entries must be updated at each balance period which simulates the arrival of new information. The MAPIT SITMUF calculation is not well vectorized as the $NxN$ must be resized and calculated at each balance. The calculation starts by looping over balance periods and each entry in the covariance matrix at balance $P$:


<span style="font-size: 1.5em; font-weight: bold;"><code>AuxFunctions.py</code></span>
```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:start-after: _covmat_loop-start
:end-before: _covmat_loop-end
:language: python
:linenos:
:lineno-match:
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
    \colorbox{#5755aa}{$\sum_{l \in l_0} \left( \left(\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i}I_{l,t}\right)^2 * ((\delta_{R,l})^2 + (\delta_{S,l})^2) \right) $} \\
        &  +  \colorbox{#0074CC}{$\sum_{l \in l_1} \left( \left( \int_{t=\text{MBP}_{i-1}}^{\text{MBP}_i} O_{l,t} \right)^2 * ((\delta_{R,l})^2 + (\delta_{S,l})^2) \right)$} \\
    & + \colorbox{#A2782A}{$\sum_{l \in l_2} \left( (C_{i,l})^2 * ((\delta_{R,l})^2 + (\delta_{S,l})^2) \right)$} \\
    & +  \colorbox{#3E8E87}{$\sum_{l \in l_2} \left( (C_{i-1,l})^2 * ((\delta_{R,l})^2 +  (\delta_{S,l})^2)  \right)$}
     -  \colorbox{#CC3300}{$\sum_{l \in l_2} \left( 2C_{i-1,l}C_{i,l}(\delta_{S,l})^2  \right)$} \\

```

<span style="color:#5755aa; font-size: 1.5em; font-weight:bold">Term 1</span>
<br>
<span style="font-size: 1.5em; font-weight: bold;"><code>AuxFunctions.py</code></span>
```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:start-after: _covmat_D1-start
:end-before: _covmat_D1-end
:language: python
:linenos:
:lineno-match:
:emphasize-lines: 6,8
```

<span style="color:#0074CC; font-size: 1.5em; font-weight:bold">Term 2</span>
<br>
<span style="font-size: 1.5em; font-weight: bold;"><code>AuxFunctions.py</code></span>

```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:start-after: _covmat_D2-start
:end-before: _covmat_D2-end
:language: python
:linenos:
:lineno-match:
:emphasize-lines: 7,9
```

<span style="color:#A2782A; font-size: 1.5em; font-weight:bold">Term 3</span>
<br>
<span style="font-size: 1.5em; font-weight: bold;"><code>AuxFunctions.py</code></span>
```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:start-after: _covmat_D345-start
:end-before: _covmat_D345-end
:language: python
:linenos:
:lineno-match:
:emphasize-lines: 7
```

<span style="color:#3E8E87; font-size: 1.5em; font-weight:bold">Term 4</span>
<br>
<span style="font-size: 1.5em; font-weight: bold;"><code>AuxFunctions.py</code></span>
```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:start-after: _covmat_D345-start
:end-before: _covmat_D345-end
:language: python
:linenos:
:lineno-match:
:emphasize-lines: 16
```

<span style="color:#CC3300; font-size: 1.5em; font-weight:bold">Term 5</span>
<br>
<span style="font-size: 1.5em; font-weight: bold;"><code>AuxFunctions.py</code></span>
```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:start-after: _covmat_D345-start
:end-before: _covmat_D345-end
:language: python
:linenos:
:lineno-match:
:emphasize-lines: 17
:caption: The factor 2 is included later when the terms are added and assigned to the covariance matrix.
```



### Off-diagonal terms

```{math}
:class: only-dark

\sigma_{i,j}^2  \approx    
    &   \colorbox{#5755aa}{$ \sum_{l \in l_0} \left( \left(\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_j}I_{t,l}\right) \left( \int_{t=\text{MBP}_{j-1}}^{\text{MBP}_j}I_{t,l} \right)  (\delta_{S,l})^2 \right)  $}\\
    + &  \colorbox{#0074CC}{$ \sum_{l \in l_1} \left( \left(\int_{t=\text{MBP}_{i-1}}^{\text{MBP}_j}O_{t,l}\right) \left( \int_{t=\text{MBP}_{j-1}}^{\text{MBP}_j}O_{t,l} \right)  (\delta_{S,l})^2 \right) $} \\
    + &  \colorbox{#A2782A}{$\sum_{l \in l_2} \left( \left(   C_{i,l}C_{j,l} + C_{i-1,l}C_{j-1,l}   \right) * (\delta_{S,l})^2 \right)$} \\
    - & \colorbox{#3E8E87}{$\sum_{l \in l_2} \left( \left(   C_{i,l}C_{j-1,l}    \right) * \left(  (\delta_{S,l})^2 + P(j-1 == i)*(\delta_{R,l})^2 \right)   \right) $}\\
    - &  \colorbox{#CC3300}{$\sum_{l \in l_2} \left( \left(   C_{i-1,l}C_{j,l}    \right) * \left(  (\delta_{S,l})^2 + P(i-1 == j)*(\delta_{R,l})^2 \right)   \right) $}\\
```

<span style="color:#5755aa; font-size: 1.5em; font-weight:bold">Term 1</span>
<br>
<span style="font-size: 1.5em; font-weight: bold;"><code>AuxFunctions.py</code></span>
```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:start-after: _covmat_OD1-start
:end-before: _covmat_OD1-end
:language: python
:linenos:
:lineno-match:
:emphasize-lines: 6,7,9,10,14,15
```

<span style="color:#0074CC; font-size: 1.5em; font-weight:bold">Term 2</span>
<br>
<span style="font-size: 1.5em; font-weight: bold;"><code>AuxFunctions.py</code></span>
```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:start-after: _covmat_OD2-start
:end-before: _covmat_OD2-end
:language: python
:linenos:
:lineno-match:
:emphasize-lines: 9,10,12,13,17,18
```

<span style="color:#A2782A; font-size: 1.5em; font-weight:bold">Term 3</span>
<br>
<span style="font-size: 1.5em; font-weight: bold;"><code>AuxFunctions.py</code></span>
```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:start-after: _covmat_OD345-start
:end-before: _covmat_OD345-end
:language: python
:linenos:
:lineno-match:
:emphasize-lines: 8-11
```

<span style="color:#3E8E87; font-size: 1.5em; font-weight:bold">Term 4</span>
<br>
<span style="font-size: 1.5em; font-weight: bold;"><code>AuxFunctions.py</code></span>
```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:start-after: _covmat_OD345-start
:end-before: _covmat_OD345-end
:language: python
:linenos:
:lineno-match:
:emphasize-lines: 13-18,21
```

<span style="color:#CC3300; font-size: 1.5em; font-weight:bold">Term 5</span>
<br>
<span style="font-size: 1.5em; font-weight: bold;"><code>AuxFunctions.py</code></span>
```{literalinclude} ../../MAPIT/core/AuxFunctions.py
:start-after: _covmat_OD345-start
:end-before: _covmat_OD345-end
:language: python
:linenos:
:lineno-match:
:emphasize-lines: 23,24,26-29,31
```


## Further reading
* [Revisiting statistical aspects of NMA - Burr](https://onlinelibrary.wiley.com/doi/10.1155/2013/961360)
* [Handbook of Nuclear Engineering: Proliferation Resistance and Safeguards](https://link.springer.com/referenceworkentry/10.1007/978-0-387-98149-9_29#Sec1_29)