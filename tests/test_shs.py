import pandas as pd
from homogeneous_segmentation import spatial_heterogeneity_segmentation
from util.dummy_data import df1


def test_shs_df1():
    py_output = spatial_heterogeneity_segmentation(
        data                         = df1,
        measure                      = ("slk_from", "slk_to"),
        variables                    = ["var_a","var_b"],
        allowed_segment_length_range = (0.020, 0.100)
    )
    r_output = pd.read_csv("./tests/r_outputs/df1_seg_test_out.csv")
    assert r_output.compare(py_output).empty


def test_shs_df2():
    df2 = pd.read_csv("./tests/test_data/df2.csv")

    df2 = df2[
          (df2["road"]=="H001")
        & (df2["cwy"]=="S")
        & (df2["dirn"]=="L")
        & (df2["slk_from"]>50)
        & (df2["slk_from"]<60)
    ]

    py_output = spatial_heterogeneity_segmentation(
        data                         = df2,
        measure                      = ("slk_from", "slk_to"),
        variables                    = ["deflection"],
        allowed_segment_length_range = (0.050, 0.200)
    ).reset_index(drop=True).sort_values(by="slk_from")
    
    r_output = pd.read_csv("./tests/R_Outputs/df2_seg_test_out.csv").reset_index(drop=True).sort_values(by="slk_from")

    assert r_output.compare(py_output).empty