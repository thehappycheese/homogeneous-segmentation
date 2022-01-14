#' Cummulative difference approach (CDA) for homogeneous segmentation of spatial lines data.
#'
#' @description Function for homogeneous segmentation of spatial lines data using
#'              a cummulative difference approach (CDA).
#'
#' @usage cda(var = "deflection", length = "length", data, range = NULL)
#'
#' @param var A character or a character vector of variable names,
#'            such as a road pavement performance indicator.
#' @param length A character of road length name in data.
#' @param data A data frame of a dataset.
#' @param range A vector of length threshold.
#'
#' @importFrom data.table as.data.table
#'
#' @examples
#' testdata <- tsdwa[1:100,]
#' testdata$Length <- testdata$SLK.end - testdata$SLK.start
#' testdata <- cda(var = "Deflection", length = "Length", testdata)
#'
#' @export

def cda():
    raise NotImplemented("TODO");