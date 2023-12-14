import pandas
import numpy as np
import numpy.typing as npt
from typing import Optional
#from matplotlib import pyplot as plt

def cumq (data:npt.ArrayLike) -> npt.ArrayLike: # debug: use cumq to calculate q values along all segment points
    """ Computes the cumulative Q-statistic for each potential split index in an array.

    The Q-statistic is a measure that quantifies the importance of each variable by
    comparing the variance of the target variable across different spatial regions
    against the overall variance in the entire study area. It is used to identify
    optimal segmentation points in the dataset where the variance within segments is
    minimized, and the variance between segments is maximized.

    Formula:

    ```
    Q = 1 - Σ(N_v,j * σ_v,j^2) / (N_v * σ_v^2)
    ```

    Where:

    - `N_v` and `σ_v^2` are the number and population variance of observations within the whole study area.
    - `N_v,j` and `σ_v,j^2` are the number and population variance of observations within the j-th sub-region.
    - `M` is the total number of sub-regions.

    Args:
        data (npt.ArrayLike): An array-like object containing the data points for which the Q values are to be computed.

    Returns:
        npt.ArrayLike: An array of the same length as 'data', containing the computed Q values for each potential split point.
    """

    # NOTE: In the original R package, `cum_n` is 1 item shorter than `data``. I am not sure if this is an error?
    #       `cum_n` is primarily used to index `data`. I use `data[:-1]` instead of `data[cum_n]` in this port.
    #       note that to preserve the original functionality data_left and data_right have been selected to drop one element from the data also
    #       see _cumq_fixed below
   
    cum_n                = np.arange(1, len(data))  # 1:(n - 1)         # Used as denominator later ∴ Must start from 1.
    assert len(cum_n) == len(data) -1               # this preserves original functionality though i think it is possibly an error?
    #data_left          <- data[cum_n]
    data_left            = data[:-1]                # drops last
    #data_right         <- rev(data)[cum_n]
    data_right           = data[::-1][:-1]          # reverses and then drops last
    
    cum_data_left        = np.cumsum(data_left)
    cum_data_right       = np.cumsum(data_right)[::-1]
    sumd                 = np.sum(data)
    cum_datasquare_left  = np.cumsum(np.power(data_left, 2))
    cum_datasquare_right = np.cumsum(np.power(data_right, 2))[::-1]

    result = (
        1 - (
              ( cum_datasquare_left - cum_data_left  * cum_data_left  / cum_n      ) 
            + (cum_datasquare_right - cum_data_right * cum_data_right / cum_n[::-1])
        ) / (
            np.sum(np.power(data, 2)) - sumd**2 / len(data)
        )
    )    
    
    # fig, (ax1,ax2) =  plt.subplots(2,1)
    # pandas.Series(data).plot(ax=ax1, ylabel="Q")
    # pandas.Series(result).plot(ax=ax2, ylabel="data")

    return result


def seg2 (data:pandas.DataFrame, var:list[str], length:str, allowed_segment_length_range:tuple[float, float]) -> list[int]:
    """
    Bisects the given data at the index of maximum Q value, calculated from the '_cumq' function.

    This function is used for finding the optimal split point in the data, based on the maximum Q value.
    It considers the allowed segment length range and operates on specified variables.

    Args:
        data (pandas.DataFrame): The DataFrame containing the data to be segmented.
        var (list[str]): A list of column names in 'data' that are to be used for segmentation.
        length (str): The column name in 'data' that represents the length of each segment.
        allowed_segment_length_range (tuple[float, float]): A tuple indicating the minimum and maximum allowed lengths for each segment.

    Returns:
        list[int]: A list of indices in 'data' where the maximum Q values are found, indicating optimal split points.
    """

    min_length, _max_length = allowed_segment_length_range

    data_var        = data[var]
    data_length     = data[length]

    cumlength_left  = np.cumsum(data[length].to_numpy())
    cumlength_right = np.cumsum(data[length].to_numpy()[::-1])[::-1]
    
    k_mask = ~ (
          (cumlength_left  <= min_length)
        | (cumlength_right <= min_length)
    )

    # to match the behaviour of the R script we must expand the false values
    # in the array by one index either side;
    # the bool series 001111000 is modified to 0001100000
    # Since cumlength_left and cumlength_right should be monotonically increasing,
    # the bool series should have at most 3 segments, with
    # contiguous sections of zero only at the start and end of the series.
    #   NOTE: numpy has no shift-and-fill function, so a shift based solution looks ugly:
    #         np.pad(k_mask, (1,0), mode="constant", constant_values=True)[:-1] & np.pad(k_mask,(0,1), mode="constant",constant_values=True)[1:]
    #         therefore I will stick with a convolve based solution:
    k_mask = ~np.convolve(~k_mask, np.full(3, True))[1:-1]
    

    
    # plt.figure()
    # (pandas.Series(k_mask,index=cumlength_left).astype("int") * 0.1).plot(color="grey", marker="x")
    # pandas.Series(cumlength_left , index=cumlength_left).plot(marker=".")
    # pandas.Series(cumlength_right, index=cumlength_left).plot(marker=".")
    # plt.axhline(min_length)


    k = np.flatnonzero(k_mask)
    
    try:
        # confirm that k_mask splits the data into three portions
        # this appears to be assumed in the R package?
        assert len(np.split(k_mask,np.flatnonzero(k_mask[:-1] != k_mask[1:])+1)) == 3
    except AssertionError:
        # if it didn't split into 3 sections, perhaps one or two segments will not 
        # print("did not split into 3... try 1 or 2?")
        assert len(np.split(k_mask,np.flatnonzero(k_mask[:-1] != k_mask[1:])+1)) in {1,2}


    qvalue_columns = []
    for each_var in var: 
        # qvalue[, i] <- _cumq(data.var[[i]])[k - 1]
        qvalue_columns.append(
            cumq(data.loc[:,each_var].values)[k_mask[1:]]
        )
    
    # qvalue = rowMeans(qvalue)
    qvalue     = np.mean(np.array(qvalue_columns), axis=0)
    
    # NOTE: This next line appears to retrieve the index of the global maximum (mean) Q value.
    #       It IS possible that it could return a list instead of a scalar
    #       The downstream code will split at every index in maxk without complaint.
    #       Thats ok, BUT there is no further check that we do not create a segment shorter
    #       than the minimum segment length.
    #       we could fix this my using np.argmax() which will return only the first maximum.
    #       for now I will leave this as-is so that results are compareable with the R code.
    # maxk <- which(qvalue == max(qvalue)) + max(k_left)
    maxk = np.flatnonzero(qvalue == np.max(qvalue)) + k[0]
    return maxk


def shs(data:pandas.DataFrame, var:list[str], length:str, allowed_segment_length_range:tuple[float, float]) -> pandas.DataFrame:
    """
    Spatial Heterogeneity-based Segmentation (SHS) for homogeneous segmentation of linear spatial data.

    This function applies SHS algorithm to linear spatial data for segmentation based on spatial heterogeneity.
    
    - maximises the variance between segments while minimising the variance within segments.
    - it iteratively splits the segments until the maximum segment length is less than the maximum allowed segment length.
    - the segmentation is stopped when the minimum segment length is less than the minimum allowed segment length.

    Args:
        data (pandas.DataFrame): The DataFrame containing spatial linear data.
        var (list[str]): Variable names to consider for segmentation, such as road pavement performance indicators.
        length (str): The column name in 'data' representing the length of road segments.
        allowed_segment_length_range (tuple[float, float]): The minimum and maximum length allowed for each segment after splitting.

    Returns:
        pandas.DataFrame: The input DataFrame with additional columns indicating segment IDs and segmentation points.
    """

    # n_var = len(var)
    min_length, max_length = allowed_segment_length_range

    # first segmentation
    ss          = seg2(data, var, length, allowed_segment_length_range)
    #ss = np.array([3,5])
    # following segmentation
    k1          = np.array([0, *ss])
    k2          = np.array([*ss, len(data.index)])
    ll          = k2 - k1
    cum_ll      = np.append(np.array([0]), np.cumsum(ll))
    segid       = np.repeat(np.arange(0, len(ll)), ll)
    #segdatalist = np.split(data, segid)

    # NOTE: We are grouping the data wherever _seg2 found a maximum Q value.
    # Generally there should be only a single maximum, but if there
    # is an equal maximum at two indices, then there will be more than 2 groups.
    # in practice this should be vanishingly rare... 
    # but in future we should come back and prevent this.
    segdatalist:list[npt.ArrayLike] = np.split(data, np.cumsum(ll)[:-1])

    #lengthdata        = pandas.DataFrame([data.loc[:,length], segid], columns = ["length","seg.id"]))
    seglength_summary = data[length].groupby(segid).sum()

    seglength         = seglength_summary.round(10).values
    k = np.flatnonzero(seglength > max_length)

    while(len(k) > 0):
        sa = [seg2(segdatalist[x], var, length, allowed_segment_length_range) + cum_ll[x] for x in k]
        ss = np.sort(np.concatenate([ss, *sa]))

        k1          = np.array([0, *ss])
        k2          = np.array([*ss, len(data.index)])
        ll          = k2 - k1
        cum_ll      = np.append(np.array([0]), np.cumsum(ll))
        segid       = np.repeat(np.arange(0, len(ll)), ll)
        #segdatalist = np.split(data, segid)

        # we are grouping the data wherever _seg2 found a maximum. generally there should be only a single maximum,
        # but if there is an equal maximum at two indices, then there will be 3 groups overall.
        segdatalist = np.split(data, np.cumsum(ll)[:-1])

        #lengthdata        = pandas.DataFrame([data.loc[:,length], segid], columns = ["length","seg.id"]))
        seglength_summary = data[length].groupby(segid).sum()

        seglength         = seglength_summary.round(10).values
        k = np.flatnonzero(seglength > max_length)
    
    # # add seg.id
    k1                          = np.array([0, *ss])
    k2                          = np.array([*ss, len(data.index)])
    ll                          = k2 - k1
    segid                       = np.repeat(np.arange(0, len(ll)), ll)
    
    data["seg.id"]              = segid + 1  # +1 for consistency with R version.
    data["seg.point"]           = 0
    data.loc[[0,*ss], "seg.point"] = 1

    return data


# TODO: this function wraps the shs function...
#       This follows the structure used in the R package,
#       but these two functions could be merged in the future.
def spatial_heterogeneity_segmentation(
        data:pandas.DataFrame,
        measure:tuple[str, str], 
        variables:list[str], 
        allowed_segment_length_range:Optional[tuple[float, float]] = None,
        segment_id_column_name = "seg.id",
        length_column_name = "length"
    ):
    """
    Homogeneous segmentation function for continuous variables, using Spatial Heterogeneity Segmentation (SHS) method.
    Modifies the input DataFrame and returns it with a column "seg.id"

    Copied from the original python port at <https://github.com/thehappycheese/HS> which was in turn
    ported from an [R package - also called HS](https://cran.r-project.org/web/packages/HS/index.html).
    The author of the original R package is **Yongze Song**, and it is related to the following paper:

    > Song, Yongze, Peng Wu, Daniel Gilmore, and Qindong Li. "[A spatial heterogeneity-based segmentation model for analyzing road deterioration network data in multi-scale infrastructure systems.](https://ieeexplore.ieee.org/document/9123684)" IEEE Transactions on Intelligent Transportation Systems (2020).

    Args:
        data (DataFrame): DataFrame to be modified
        measure (tuple[str,str]): Names of column indicating start SLK (linear / spatial measure). eg ("slk_from", "slk_to")
        variables (list[str]): A list of column names referring to the continuous numeric variables to be used by the segmentation method. eg ["roughness","deflection"]
        allowed_segment_length_range (Optional[tuple[float,float]]):  Maximum and minimum segment lengths.
            Note that rows will not be split if they are already larger than the minimum. 
            If nothing is provided then the min length of existing segments will be used as minimum
            and the sum of all segment lengths will be used as the maximum.
            This function only groups rows by adding the index column "seg.id"
        segment_id_column_name (str): Name of the column to be added to the DataFrame. Defaults to "seg.id"
        length_column_name (str): Name of the column to be added to the DataFrame. Defaults to "length"
        
    Returns:
        The original DataFrame with new columns `'length'`, `'seg.id'` and `'seg.point'`
        `'seg.id'` is an integer, and `'seg.point'` is zero everywhere except for the start of a new segment.
        `'length'` is the length of each segment in the same units as the `measure`.

    """

    measure_start, measure_end = measure

    # preprocessing
    data = (
        data
        .dropna(subset=variables)
        .sort_values(by=measure_start)
        .reset_index(drop=True)
    )

    # add length # remove system errors of small data
    data[length_column_name] = (data[measure_end] - data[measure_start]).round(decimals=10)

    if allowed_segment_length_range is None:
        allowed_segment_length_range = (
            data[length_column_name].min(),
            data[length_column_name].sum()
        )

    if data[length_column_name].sum() <= allowed_segment_length_range[1]:
        data[segment_id_column_name] = 1
    else:	
        data = shs(data, var = variables, length = length_column_name, allowed_segment_length_range = allowed_segment_length_range)

    return data
