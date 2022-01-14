#' Homogeneous segmentation function with continuous variables.
#'
#' @usage hs(start = "SLK.start", end = "SLK.end", var = "deflection",
#'           data, method = "shs", range = NULL)
#'
#' @param start A character of start location name of a spatial line.
#' @param end A character of end location name of a spatial line.
#' @param var A character or a character vector of variable names,
#'            such as a road pavement performance indicator.
#' @param data A data frame of a dataset.
#' @param method A character of homogeneous segmentation method.
#'               Available methods include "shs", "cda" and "mcv".
#' @param range A vector of segment length threshold.
#'
#' @importFrom utils capture.output
#' @importFrom stats aggregate complete.cases median quantile sd
#' @importFrom grDevices hcl
#'
#' @examples
#' testdata <- tsdwa[1:100,]
#' hs1 <- hs(start = "SLK.start", end = "SLK.end", var = c("Curvature", "Deflection", "BLI"),
#'           testdata, method = "shs", range = c(0.1, 0.5))
#'
#' @export

from typing import Literal, Optional
import pandas

from .util.preprocessing import preprocessing

from .util.shs import shs
from .util.mcv import mcv
from .util.cda import cda
from .util.splitlong import splitlong

# TODO: reorder parameters; data should be first as it has no default.
def hs (
		data:pandas.DataFrame, method:Literal["shs","mcv","cda"] = "shs", 
		start:str = "SLK.start", 
		end:str = "SLK.end", 
		var:list[str] = ["deflection"], 
		allowed_segment_length_range:Optional[tuple[float, float]] = None
	):

	data = preprocessing(data, var = var, location = start)

	# add length # remove system errors of small data
	data["length"] = (data[end] - data[start]).round(decimals=10)

	if allowed_segment_length_range is None:
		allowed_segment_length_range = (
			data["length"].min(),
			data["length"].sum()
		)

	if data["length"].sum() <= allowed_segment_length_range[1]:
		data["seg.id"] = 1
	else:
		# multiple observation variables
		if   method == "shs":
			data = shs(data, var = var, length = "length", allowed_segment_length_range = allowed_segment_length_range)

		elif method == "mcv":
			data = mcv(data, var = var, length = "length", range = allowed_segment_length_range)

		elif method == "cda":
			data = cda(data, var = var, length = "length", range = allowed_segment_length_range)
			data = splitlong(data, var = var, length = "length", seg_id = "seg.id", range = allowed_segment_length_range)

		else:
			raise Exception("Available methods include 'shs', 'mcv' and 'cda'.")
	

	return data