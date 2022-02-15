


import pandas
import numpy as np
CATEGORY_COLUMN_NAME = "seg.ctg"



def segment_by_category_and_slk_breaks(
        data:pandas.DataFrame,
        categories:list[str]=["road", "cwy"],
        measure_from:str="slk_from",
        measure_to:str="slk_to",
    ):
    """
    Segments data by multiple categories, and any time slk experiences a discontinuity.
    Segmentation is achieved by adding a column called "seg.id" to the original dataframe and returning it.

    This function was not part of the original HS R package.
    This function works well for some use cases (when there are gaps in the SLK measure),
    but there are issues with SLK overlaps. For overlaps we must either depend on original sort order
    as extracted from Main Roads systems, or we must improve this function to look at both SLK and True Distance 
    fields to establish correct segmentation points.

    Furthermore, when we try to merge datasets downstream, it will be necessary to not only have 
    segmentation id, but also intact slk_from, slk_to, true_from and true_to to correctly merge.
    """
    
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


def segment_by_category_and_slk_true_breaks(
        data:pandas.DataFrame,
        categories:list[str]=["road", "cwy"],
        measure_slk:tuple[str,str]=("slk_from", "slk_to"),
        measure_true:tuple[str,str]=("true_from", "true_to"),
    ):
    """
	# segment_by_category_and_slk_true_breaks
	
    Segments data by multiple categories, and any time slk or true experiences a discontinuity.

    > Note:
    >
	> - the range `true_from` to `true_to` for observations must be **non-overlapping**.
	> - no check is made for overlaping observations.

    Segmentation is achieved by adding a column called "seg.id" to the original dataframe and returning it.

    This function was not part of the original HS R package.
    This function works well for some use cases (when there are gaps in the SLK measure),
    but there are issues with SLK overlaps. For overlaps we must either depend on original sort order
    as extracted from Main Roads systems, or we must improve this function to look at both SLK and True Distance 
    fields to establish correct segmentation points.

    Furthermore, when we try to merge datasets downstream, it will be necessary to not only have 
    segmentation id, but also intact slk_from, slk_to, true_from and true_to to correctly merge.

	Args:
		data: pandas.DataFrame
		categories: list[str]
		measure_slk: tuple[str,str]
		measure_true: tuple[str,str]
    """
    
    measure_slk_from, measure_slk_to = measure_slk
    measure_true_from, measure_true_to = measure_true


    data = data.sort_values(by=[*categories, measure_true_from])
    result_column = data.set_index(categories).loc[:,[]]

    offset = 0
    for group_index, group in data.groupby(categories):

        cat_values = np.cumsum(
            np.append(
                np.full(1,False),
                (   
                       np.around(group[  measure_slk_to].values[ :-1], 3)
                    != np.around(group[measure_slk_from].values[1:  ], 3)
                )
                |
                (   
                       np.around(group[  measure_true_to].values[ :-1], 3)
                    != np.around(group[measure_true_from].values[1:  ], 3)
                )
            )
        )

        result_column.loc[group_index, CATEGORY_COLUMN_NAME] = cat_values + offset
        offset += max(cat_values)+1
    
    data[CATEGORY_COLUMN_NAME] = result_column.values.astype("int")

    return data