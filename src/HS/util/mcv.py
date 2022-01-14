#' Minimization coefficient of variation (MCV) for homogeneous segmentation of spatial lines data.
#'
#' @usage mcv(var = "deflection", length = "length", data, range = NULL)
#'
#' @param var A character or a character vector of variable names,
#'            such as a road pavement performance indicator.
#' @param length A character of road length name in data.
#' @param data A data frame of a dataset.
#' @param range A vector of segment length threshold.
#'
#' @examples
#' testdata <- tsdwa[1:100,]
#' testdata$length <- testdata$SLK.end - testdata$SLK.start
#' testdata <- mcv(var = "Deflection", length = "length", testdata, range = c(0.1, 0.5))
#'
#' @export


def mcv():
    raise NotImplemented("TODO")