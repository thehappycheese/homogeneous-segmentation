from typing import Optional
import pandas as pd
from ._optimal_bisections import optimal_bisections

import numpy as np
import numpy.typing as npt

def cumulative_p(data:npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    cum_n                = np.arange(1, len(data))  # 1:(n - 1)         # Used as denominator later ∴ Must start from 1.
    cum_n_rev            = cum_n[:  :-1]
    data_left            = data [:-1   ]            # drops last
    data_right           = data [:0 :-1]            # reverses and then drops last
    cum_data_left        = np.cumsum(data_left      )
    cum_data_right       = np.cumsum(data_right     )[::-1]
    cum_datasquare_left  = np.cumsum(data_left  ** 2)
    cum_datasquare_right = np.cumsum(data_right ** 2)[::-1]
    return (
            (
                  (cum_n     * cum_datasquare_left  / (cum_data_left  * cum_data_left ) - 1)
                *  cum_n
                / (cum_n     - 1)
            )**0.5
        +   (
                  (cum_n_rev * cum_datasquare_right / (cum_data_right * cum_data_right) - 1)
                *  cum_n_rev
                / (cum_n_rev - 1)
            )**0.5
    ) / 2