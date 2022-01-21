
import pandas as pd
from HS.util.segbycategory import segbycategory

def test_segbycategory():
    
    #data[CATEGORY_COLUMN_NAME] = data.groupby(by_category).ngroup() + 1

    df = pd.read_csv("./test/test_data/df2.csv")
    df = segbycategory(
        df,
        ["road","cwy","dirn"]
    )
    r_output = pd.read_csv("./test/r_outputs/df2_segcat_out.csv")
    assert r_output.compare(df).empty

