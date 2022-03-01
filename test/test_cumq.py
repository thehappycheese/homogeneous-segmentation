


def test_cumq():
    from HS.shs import _cumq
    from util.dummy_data import df1
    import numpy as np

    assert sub_test_cumq(df1["var_a"].values)
    assert sub_test_cumq(df1["var_b"].values)

def sub_test_cumq(data):
    from HS.shs import _cumq
    from util.dummy_data import df1
    import numpy as np

    result = _cumq(data)
    result_slow = []
    divisor = np.var(data) * len(data)
    for index in range(1, len(data)):
        da = data[:index]
        db = data[index:]
        result_slow.append(
            1 - (len(da) * np.var(da) + len(db)* np.var(db)) / divisor
        )
    return ((np.array(result_slow) - result) < 0.0000001).all()
    