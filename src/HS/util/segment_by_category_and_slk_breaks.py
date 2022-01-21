


import pandas
import numpy as np
CATEGORY_COLUMN_NAME = "seg.ctg"

def segment_by_category_and_slk_breaks(
        data:pandas.DataFrame,
        categories:list[str]=["road", "cwy"],
        measure_from:str="slk_from",
        measure_to:str="slk_to",
    ):
    
    data = data.sort_values(by=[*categories, measure_from])
    result_column = data.set_index(categories).loc[:,[]]

    offset = 0
    for group_index, group in data.groupby(categories):

        cat_values = np.cumsum(
            np.append(
                np.full(1,False),
                   np.around(group[  measure_to].values[ :-1], 3)
                != np.around(group[measure_from].values[1:  ], 3)
            )
        )

        result_column.loc[group_index, CATEGORY_COLUMN_NAME] = cat_values + offset
        offset += max(cat_values)+1
    
    data[CATEGORY_COLUMN_NAME] = result_column.values.astype("int")

    return data