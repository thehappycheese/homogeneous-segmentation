from typing import Literal, Optional
import pandas

from .util.shs import shs
from .util.mcv import mcv
from .util.cda import cda
from .util.splitlong import splitlong



SEGMENT_ID_COLUMN_NAME = "seg.id"

def homogenous_segmentation (
		data:pandas.DataFrame,
		method:Literal["shs","mcv","cda"] = "shs", 
		measure_start:str = "SLK.start", 
		measure_end:str = "SLK.end", 
		variables:list[str] = ["deflection"], 
		allowed_segment_length_range:Optional[tuple[float, float]] = None
	):
	"""
	Homogeneous segmentation function with continuous variables.
	Modifies the input dataframe and returns it with a column "seg.id"

	Args:
		data (DataFrame): Dataframe to be modified
		measure_start (str): Name of column indicating start SLK (linear / spatial measure)
		measure_end (str): Name of column indicating end SLK (linear / spatial measure)
		variables (list[str]): A list of column names refering to the continuous numeric variables to be used by the segmentation method (eg roughness or deflection)
		method (str): Homogeneous segmentation method. Available methods include "shs" ("cda" and "mcv" may be implemented later).
		allowed_segment_length_range (tuple[float,float]):  Maximum and minimumum segment lenghts. Note that rows will not be split if they are already larger than the minimum. This function only groups rows by adding the index column "seg.id"

	Returns:
	    The original dataframe with new columns `'seg.id'` and `'seg.point'`.
		`'seg.id'` is an integer, and `'seg.point'` is zero everywhere except for the start of a new segment.

	"""

	# preprocessing
	data = (
		data
		.dropna(subset=variables)
		.sort_values(by=measure_start)
		.reset_index(drop=True)
	)

	# add length # remove system errors of small data
	data["length"] = (data[measure_end] - data[measure_start]).round(decimals=10)

	if allowed_segment_length_range is None:
		allowed_segment_length_range = (
			data["length"].min(),
			data["length"].sum()
		)

	if data["length"].sum() <= allowed_segment_length_range[1]:
		data[SEGMENT_ID_COLUMN_NAME] = 1
	else:
		# multiple observation variables
		if   method == "shs":
			data = shs(data, var = variables, length = "length", allowed_segment_length_range = allowed_segment_length_range)

		elif method == "mcv":
			data = mcv(data, var = variables, length = "length", range = allowed_segment_length_range)

		elif method == "cda":
			data = cda(data, var = variables, length = "length", range = allowed_segment_length_range)
			data = splitlong(data, var = variables, length = "length", seg_id = SEGMENT_ID_COLUMN_NAME, range = allowed_segment_length_range)

		else:
			raise Exception("Available methods include 'shs', 'mcv' and 'cda'.")
	

	return data



def homogenous_segmentation_with_categories (
		data:pandas.DataFrame,
		method:Literal["shs","mcv","cda"] = "shs", 
		start:str = "SLK.start", 
		end:str = "SLK.end", 
		variables:list[str] = ["deflection"], 
		categories:list[str] = ["road","cwy"],
		allowed_segment_length_range:Optional[tuple[float, float]] = None
	):
	"""
	NOT IMPLEMENTED
	Homogeneous segmentation function with both categories and continuous variables.
	Modifies the input dataframe and returns it.

	Args:
		data (DataFrame): Dataframe to be modified
		measure_start (str): Name of column indicating start SLK (linear / spatial measure)
		measure_end (str): Name of column indicating end SLK (linear / spatial measure)
		variables (list[str]): A list of column names refering to the continuous numeric variables to be used by the segmentation method (eg roughness or deflection)
		categories (list[str]): A list of column names refering to the categorical variables intowhich the data should be segmented prior to the main segmentation method
		method (str): Homogeneous segmentation method. Available methods include "shs" ("cda" and "mcv" may be implemented later).
		allowed_segment_length_range (tuple[float,float]):  Maximum and minimumum segment lenghts. Note that rows will not be split if they are already larger than the minimum. This function only groups rows by adding the index column "seg.id"

	Returns:
	    The original dataframe with new columns `'seg.id'` and `'seg.point'`.
		`'seg.id'` is an integer, and `'seg.point'` is zero everywhere except for the start of a new segment.

	"""

	raise NotImplemented("TODO")