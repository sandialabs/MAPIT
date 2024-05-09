# StatsProcessor
---

## Overview

The `StatsProcessor` module contains the `MBArea` object, which is the foundation of the MAPIT API.
 The first step in using MAPIT is to define a material balance area (i.e., `MBArea`). This object takes a 
 number of parameters that are used to define a material balance area. The initial properties can
  be later modified by accessing the specific object properties.

After the `MBArea` is successfully defined, different statistical tests can be applied to
the `MBArea` by calling object methods. The results are returned after calling the method,
but results are also stored as object attributes that can be easily accessed. 
   
:::{tip}
The `MBArea` object is designed to streamline the analysis experience while
providing flexibility. For example, a `MBArea` could be initialized, copied,
then have a few properties modified to compare "what-if" scenarios. 
```python
# initalize with some variables
MBA0 = MBArea(...) 

# clone MBArea
MBA1 = copy.copy(MB0) 

# modify input term errors
MBA1.inputErrorMatrix = otherErrorMatrix 

# calculate sigma MUF
MBA0.SEMUF()
MBA1.SEMUF()

# do comparison between baseline and modified input error cases
# ...
```
:::

:::{important}
If modifying the error matrix *after* having calculated errors or a statistical quantity, the errors must be recalculated using the `calcErrors` method. 
:::

## Parallel Processing

MAPIT provides parallel processing capabilities through the (Ray)[https://www.ray.io/] library. By default, Ray provides a local dashboard at [127.0.0.1:8265](http://127.0.0.1:8265) which can be used to monitor progress and view job related statistics. Two key parameters are used for parallel processing; `ncpu` and `nbatch`. `ncpu` controls the number of CPUs provided to Ray whereas `nbatch` is the number of iterations to process for each task. Once provided, each Ray worker (total is equal to `ncpu`) works through a queue of tasks. Each task returns some of the iterations requested by the user (defined by `nbatch`) until all results are processed. A table showing the relationship between user specified variables `iterations`, `ncpu`, and `nbatch` the number of tasks performed by each worker is shown below. Workers process tasks in the queue until the queue is completed. 

| `iterations` | `ncpu` | `nbatch` | total number of tasks | tasks completed per worker |
|  :---:  |  :---:  |  :---:  |  :---:  | :---:  |
| 100 | 5 | 1 | 100 | 20 |
| 100 | 5 | 5 | 20 | 4 |
| 100 | 5 | 20 | 5 | 1 |

`nbatch` is provided as a parameter as there is overhead incurred when copying data to/from workers. If `nbatch` is too small, then parallel processing might be slower than sequential processing if the calculation time is small compared to the memory copying time. We do not provide guidance on setting these parameters as performance will be system specific. 

---

## Classes

```{eval-rst}  
.. automodule:: MAPIT.core.StatsProcessor
   :members:
```