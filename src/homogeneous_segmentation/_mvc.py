from typing import Optional
import pandas as pd
from ._optimal_bisections import optimal_bisections

import numpy as np
import numpy.typing as npt

def p_cumulative(data:npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
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

def minimize_coefficient_of_variation(
        data:pd.DataFrame,
        measure:tuple[str, str], 
        variables:list[str], 
        allowed_segment_length_range:Optional[tuple[float, float]] = None,
    )->pd.Series:
    """
    Homogeneous segmentation function for continuous variables, using 'Minimum Coefficient of Variation' (MCV).

    Copied from the original python port at <https://github.com/thehappycheese/HS> which was in turn
    ported from an [R package - also called HS](https://cran.r-project.org/web/packages/HS/index.html).
    The author of the original R package is **Yongze Song**, and it is related to the following paper:

    `Song, Yongze, Peng Wu, Daniel Gilmore, and Qindong Li. "[A spatial heterogeneity-based segmentation model for
    analyzing road deterioration network data in multi-scale
    infrastructure systems.](https://ieeexplore.ieee.org/document/9123684)" IEEE Transactions on Intelligent
    Transportation Systems (2020).`
    """

    measure_start, measure_end = measure
    original_index = data.index

    # preprocessing
    data = (
        data
        .dropna(subset=variables)
        .sort_values(by=measure_start)
        .reset_index(drop=True)
    )

    # add length # remove system errors of small data
    data["___length___"] = (data[measure_end] - data[measure_start]).round(decimals=10).values

    if allowed_segment_length_range is None:
        allowed_segment_length_range = (
            data["___length___"].min(),
            data["___length___"].sum()
        )

    if data["___length___"].sum() <= allowed_segment_length_range[1]:
        return pd.Series(
            data = np.ones(len(data.index), dtype=np.int64),
            index = data.index,
        )
    else:
        return pd.Series(
            index = original_index,
            data  = shs(
                data                         = data,
                variable_column_names        = variables,
                length_column_name           = "___length___",
                allowed_segment_length_range = allowed_segment_length_range,
            )
        )