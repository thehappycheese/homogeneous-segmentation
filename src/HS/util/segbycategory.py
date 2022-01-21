

from typing import Optional
import pandas
import numpy as np
from deprecated import deprecated

CATEGORY_COLUMN_NAME = "seg.ctg"

# TODO: in the future this could be implemented to return a column
#       rather than modify the original dataframe?
#       Can this function be replaced by a single DataFrame.groupby() call?


@deprecated(version="1.1.2", reason="Can be replaced by a single pandas function call; data.groupby(by_category).ngroup(). Note that order will be different to old R script behavior; However note that .ngroup() is not sensitive to original sort order nor does it preserve it. Downstream code may have to be replaced.")
def segbycategory(data:pandas.DataFrame, by_category:Optional[list[str]] = None):
    """
    Adds a column to the dataframe called 'seg.ctg' where each row is assigned 
    an id number based on the unique combinations of the values in the 
    columns listed in `by_category`

    Args:
        data (DataFrame): The dataframe to be modified
        by_category (list[str]): A list of column names

    Returns:
        DataFrame: the modified dataframe
    
    Example:

        >>> df = segbycategory(df, ["road","cwy","xsp"])
        >>> df["seg.ctg"]
    """

    if CATEGORY_COLUMN_NAME in data.columns:
        raise Exception(f"DataFrame already has a column '{CATEGORY_COLUMN_NAME}'. Unable to proceed.")

    if by_category is None or by_category==[]:
        data[CATEGORY_COLUMN_NAME] = 1
    else:

        ## solution 1
        # this alternate implementation preserves the sort order when assigning indices to categories.
        # i don't know if sort order is important downstream, but i suspect we don't need it.

        # combo_lookup = (
        #     data
        #     .loc[:, by_category]
        #     .drop_duplicates()
        #     .set_index(by_category)
        # )
        # combo_lookup.insert(0, CATEGORY_COLUMN_NAME, np.arange(1, len(combo_lookup)+1))
        # data = (
        #     data
        #     .join(
        #         combo_lookup,
        #         on=by_category,
        #     )
        # )

        ## solution 2
        # could be replaced with this; except the order of the indices assigned would be different
        #data[CATEGORY_COLUMN_NAME] = data.groupby(by_category).ngroup() + 1

        ## solution 3
        # the above two solutions do not replicate the behavior in the
        # R library because they assign a single index to each unique combination 
        # of the columns `by_category`. The R script assigns a new index every time 
        # any one of the columns changes value

        category_columns = data.loc[:, by_category]

        data[CATEGORY_COLUMN_NAME] = (
            np.append(
                np.full(1, False),
                np.any(
                       category_columns[ :-1].values
                    != category_columns[1:  ].values,
                    axis=1
                )
            )
            .cumsum()
            + 1
        )
        
    return data


