
from re import M
from HS.homogeneous_segmentation import hs
from util.dummy_data import df1

import pandas as pd
import os

def test_shs_df1():
    py_output = hs(
        data   =df1,
        method ="shs",
        start  ="slk_from",
        end    ="slk_to",
        var    =["var_a","var_b"],
        allowed_segment_length_range=(0.020, 0.100)
    )
    r_output = pd.read_csv("./test/r_outputs/df1_seg_test_out.csv")
    assert r_output.compare(py_output).empty

def test_shs_df2():


    df2 = pd.read_csv("./test/test_data/df2.csv")

    df2 = df2[
          (df2["road"]=="H001")
        & (df2["cwy"]=="S")
        & (df2["dirn"]=="L")
        & (df2["slk_from"]>50)
        & (df2["slk_from"]<60)
    ]

    py_output = hs(
        start = "slk_from",
        end = "slk_to",
        var = ["deflection"],
        data = df2,
        method = "shs",
        allowed_segment_length_range = (0.050, 0.200)
    ).reset_index(drop=True).sort_values(by="slk_from")
    
    r_output = pd.read_csv("./test/R_Outputs/df2_seg_test_out.csv").reset_index(drop=True).sort_values(by="slk_from")

    assert r_output.compare(py_output).empty