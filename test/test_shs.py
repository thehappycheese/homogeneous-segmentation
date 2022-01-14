
from HS.homogeneous_segmentation import hs
from util.dummy_data import df1

def test_shs():
    hs(df1, "shs", "slk_from", "slk_to", ["var_a","var_b"], allowed_segment_length_range=(0.020, 0.100))
    print(hs)