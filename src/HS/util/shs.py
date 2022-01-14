

import pandas
import numpy as np
import numpy.typing as npt



def _cumq (data:npt.ArrayLike) -> npt.ArrayLike: # debug: use cumq to calculate q values along all segment points
   
    # NOTE: In the original cum_n is used to index data, resulting in a reduction in series length by 1.
    #       I am not sure if this is an error?
    #       note that to preserve the original functionality data_left and data_right have been selected to drop one element from the data also
   
    cum_n                = np.arange(1, len(data))  # 1:(n - 1)         # Used as denominator later ∴ Must start from 1.
    assert len(cum_n) == len(data) -1               # this preserves original functionality though i think it is possibly an error?
    #data_left          <- data[cum_n]
    data_left            = data[:-1]                # or data[0:n - 1]   # Drops last
    #data_right         <- rev(data)[cum_n]
    data_right           = data[::-1][:-1]          # or data[-2::-1]    # Drops first and reverses

    # The following corrects the error:
    #cum_n                = np.arange(len(data)) + 1
    #assert len(cum_n) == len(data) 
    #data_left            = data
    #data_right           = data[::-1]
    
    cum_data_left        = np.cumsum(data_left)
    cum_data_right       = np.cumsum(data_right)[::-1]
    sumd                 = np.sum(data)
    cum_datasquare_left  = np.cumsum(np.power(data_left, 2))
    cum_datasquare_right = np.cumsum(np.power(data_right, 2))[::-1]

    return (
        1 - (
              ( cum_datasquare_left - cum_data_left  *  cum_data_left / cum_n      ) 
            + (cum_datasquare_right - cum_data_right * cum_data_right / cum_n[::-1])
        ) / (
            np.sum(np.power(data, 2)) - sumd**2 / len(data)
        )
    )


def _seg2 (data:pandas.DataFrame, var:list[str], length:str, allowed_segment_length_range:tuple[float, float]):
    
    min_length, _max_length = allowed_segment_length_range

    data_var        = data[var]
    data_length     = data[length]

    cumlength_left  = np.cumsum(data[length].to_numpy())
    cumlength_right = np.cumsum(data[length].to_numpy()[::-1])[::-1]

    # all of this can be skipped
    ## k_left        <- c(1, which(cumlength_left <= min_length) + 1)
    #k_left          =                   np.append(np.array([0]), np.flatnonzero((cumlength_left <= min_length).to_numpy()) + 1)
    ## k_right       <- nrow(data_var) - c(0, which(cumlength_right <= min_length))
    #k_right         = len(data.index) - np.append(np.array([1]), np.flatnonzero((cumlength_right <= min_length).to_numpy()))
    ## k             = c(1:nrow(data.var))[-c(k_left, k_right)]
    #k               = np.delete(np.arange(0, len(data.index), np.append(k_left, k_right)))
    
    k_mask = ~ (
          (cumlength_left <=min_length)
        | (cumlength_right<=min_length)
    )

    k = np.flatnonzero(k_mask)

    # confirm that k_mask splits the data into three portions
    try:
        assert len(np.split(k_mask,np.flatnonzero(k_mask[:-1] != k_mask[1:])+1)) == 3
    except AssertionError:
        print("did no split into 3... try 1 or 2?")
        assert len(np.split(k_mask,np.flatnonzero(k_mask[:-1] != k_mask[1:])+1)) in {1,2}


    qvalue_columns = []
    for each_var in var: 
        # the ` - 1` in the original ar code below appears to be compensating for error in _cumq. otherwise k would be able to take from beyond the end of the array returned from cumq
        # qvalue[, i] <- _cumq(data.var[[i]])[k - 1]
        qvalue_columns.append(
            # perpetuating the error described above
            _cumq(data.loc[:,each_var].to_numpy())[k_mask[1:]]
            # fixing the error:
            #_cumq(data.loc[:,each_var].to_numpy())[k_mask]
        )
    qvalue     = np.concatenate(qvalue_columns, axis=1)
    # qvalue = rowMeans(qvalue)
    qvalue_col = np.mean(qvalue, axis=1)
    
    # This next line appears to retrieve the index of the global maximum mean q value.
    # however there is a danger that it could return a list instead of a scalar
    # # maxk <- which(qvalue == max(qvalue)) + max(k_left)
    # maxk = np.flatnonzero(qvalue_col == qvalue_col.max()) + k_left.max()
    maxk = np.argmax(qvalue_col) + min(0, k[0]-1)
    return maxk


def _cumq_fixed (data:npt.ArrayLike) -> npt.ArrayLike: # debug: use cumq to calculate q values along all segment points
 
    cum_n                = np.arange(len(data)) + 1   # Used as denominator later ∴ Must start from 1.
    assert len(cum_n) == len(data)
    #data_left          <- data[cum_n]
    data_left            = data
    #data_right         <- rev(data)[cum_n]
    data_right           = data[::-1]

    cum_data_left        = np.cumsum(data_left)
    cum_data_right       = np.cumsum(data_right)[::-1]
    sumd                 = np.sum(data)
    cum_datasquare_left  = np.cumsum(np.power(data_left, 2))
    cum_datasquare_right = np.cumsum(np.power(data_right, 2))[::-1]

    return (
        1 - (
              ( cum_datasquare_left - cum_data_left  *  cum_data_left / cum_n      ) 
            + (cum_datasquare_right - cum_data_right * cum_data_right / cum_n[::-1])
        ) / (
            np.sum(np.power(data, 2)) - sumd**2 / len(data)
        )
    )






def _seg2_fixed (data:pandas.DataFrame, var:list[str], length:str, allowed_segment_length_range:tuple[float, float]):
    
    min_length, _max_length = allowed_segment_length_range

    data_var        = data[var]
    data_length     = data[length]

    cumlength_left  = np.cumsum(data[length].to_numpy())
    cumlength_right = np.cumsum(data[length].to_numpy()[::-1])[::-1]
    
    k_mask = ~ (
          (cumlength_left <=min_length)
        | (cumlength_right<=min_length)
    )

    k = np.flatnonzero(k_mask)

    # confirm that k_mask splits the data into three portions
    try:
        assert len(np.split(k_mask,np.flatnonzero(k_mask[:-1] != k_mask[1:])+1)) == 3
    except AssertionError:
        print("did no split into 3... try 1 or 2?")
        assert len(np.split(k_mask,np.flatnonzero(k_mask[:-1] != k_mask[1:])+1)) in {1,2}


    qvalue_columns = []
    for each_var in var: 
        qvalue_columns.append(
            _cumq_fixed(data.loc[:,each_var].to_numpy())[k_mask]
        )
    qvalue     = np.concatenate(qvalue_columns, axis=1)
    qvalue_col = np.mean(qvalue, axis=1)
    
    maxk = np.argmax(qvalue_col) + min(0, k[0]-1)
    return maxk

"""
Spatial heterogeneity-based segmentation (SHS) for homogeneous segmentation of spatial lines data.

@usage shs(var = "deflection", length = "length", data, range = NULL)

@param var A character or a character vector of variable names,
						such as a road pavement performance indicator.
@param length A character of road length name in data.
@param data A data frame of a dataset.
@param range A vector of segment length threshold.

@examples
testdata = tsdwa[1:100,]
testdata$length = testdata$SLK.end - testdata$SLK.start
testdata = shs(var = "Deflection", length = "length", testdata, range = c(0.1, 0.5))
"""

def shs (data:pandas.DataFrame, var:list[str], length:str, allowed_segment_length_range:tuple[float, float]) -> pandas.DataFrame:
    
    # n_var = len(var)
    min_length, max_length = allowed_segment_length_range

    
    # first segmentation
    ss          = _seg2_original(data, var, length, allowed_segment_length_range)
    # following segmentation
    k1          = pandas.Series([1, ss])
    k2          = pandas.Series([ss - 1, len(data.index)])
    ll          = k2 - k1 + 1
    cum_ll      = (0, *ll.cumsum())
    segid       = list(range(0, len(ll))) * ll
    segdatalist = np.split(data, segid)

    #lengthdata        = pandas.DataFrame([data.loc[:,length], seg.id], columns = ["length","seg.id"]))
    #seglength_summary = lengthdata[, .(sum(length)), by = .(seg.id)]
    #seglength         = round(seglength_summary[[2]], digits = 10)
    #k = which(seglength > max_length)

    # while(len(k) > 0){
    #     sa = sapply(k, function(x){
    #         seg2(segdatalist[[x]], min_length) + cum_ll[x]
    #     })
    #     ss = sort(c(ss, sa))

    #     k1 = c(1, ss)
    #     k2 = c(ss - 1, nrow(data))
    #     ll = k2 - k1 + 1
    #     cum_ll = c(0, cumsum(ll))
    #     segid = c(rep(1:len(ll), ll))
    #     segdatalist = split(data, segid)
    #     lengthdata = as.data.table(cbind(length = data[[length]], seg.id = segid))
    #     seglength.summary = lengthdata[, .(sum(length)), by = .(seg.id)]
    #     seglength = round(seglength.summary[[2]], digits = 10)
    #     k = which(seglength > max_length)
    # }
    # # add seg.id
    # k1 = c(1, ss)
    # k2 = c(ss - 1, nrow(data))
    # ll = k2 - k1 + 1
    # data$seg.id = rep(1:len(ll), ll)
    # data$seg.point = 0
    # data$seg.point[c(1, ss)] = 1

    return data