# Road Network Segmentation

This is a collection of python packages for road network segmentation.

Original work by Song et al ported to python by thehappycheese.

## Background

Segmentation refers to the spatial-linear indexing of road data to the physical road network. Sometimes data is available at constant interval length (e.g. every 10 metres for roughness), and must be grouped into larger intervals. Sometimes data has uneven intervals (eg  local government area) and must be split and regrouped.

The aim of this package is to help break apart and group road segments based on multiple road condition variables and categories such that each segment can be reasonably represented by a single characteristic value.



## Code ported from R

Currently this repo only contains code ported to python from R.

The HS library from <https://cran.r-project.org/web/packages/HS/index.html> has been partially ported. It is published under the GPL license which I think makes this python package GPL also. The related academic paper is titled: _Spatial Heterogeneity-Based Segmentation Model for Analyzing Road Deterioration Network Data in Multi-Scale Infrastructure Systems_

Currently only the `hs()` function where `method='shs'` has been ported.

Some tests on hand-made and real data have been implemented for the `shs` function to show that results are equivalent in R and Python.

## References

_Song, Yongze, Peng Wu, Daniel Gilmore, and Qindong Li. "A spatial heterogeneity-based segmentation model for analyzing road deterioration network data in multi-scale infrastructure systems." IEEE Transactions on Intelligent Transportation Systems (2020)._


