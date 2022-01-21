from deprecated import deprecated
import pandas


@deprecated(version="1.1.2", reason="this opperation is now embedded in the only calling function. To be removed in next version.")
def preprocessing(data:pandas.DataFrame, var:list[str] = ["deflection"], location:str = "SLK"):

	result:pandas.DataFrame = (
		data
		.dropna(subset=var)
		.sort_values(by=location)
		.reset_index(drop=True)
	)
	
	rows_removed = len(data.index) - len(result.index)

	if rows_removed > 0:
		print("${rows_removed} rows of missing data are removed.")

	return result
