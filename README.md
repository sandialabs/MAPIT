# Material Accountancy Performance Indicator Toolkit (MAPIT)


## Purpose
MAPIT is a toolkit written based in Python designed to function as a desktop application to aid in safeguards analysis of bulk materials. The inherent flexibility is designed to allow safeguards practitioners ask the "what if?" questions and to provide transparency into commonly employed statistical tests.

### Features

* Flexible I/O tools to allow analysis on a wide range of datasets
  * Permits analysis for datasets collected with non-uniform sample times
  * .csv or .mat file types


* Tutorial dataset generated from a Separations and Safeguards Performance Model ([1](https://www.osti.gov/biblio/1375573-integration-sspm-stage-mpact-virtual-facility-distributed-test-bed),[2](https://www.osti.gov/biblio/1646073-separations-safeguards-performance-model-sspm-capabilities-application-integration),[3](https://www.osti.gov/biblio/1476138-bulk-handling-facility-modeling-simulation-safeguards-analysis)) fuel fabrication model based on IAEA STR-150 ([4](https://inis.iaea.org/search/search.aspx?orig_q=RN:17037216))

* Automated error propagation


* Automated calculation of common safeguards statistical tests
  * Material Unaccounted For (MUF) / Inventory Difference (ID)
  * Standard Error of MUF (sigma MUF) / Standard Error of ID (SEID)
  * Standardized Independent Transformed MUF (SITMUF)
  * Page's Trend Test on SITMUF


* Built in threshold optimization tools
* Visualization tools
* Data export capabilities



## Library
### Information
[![platform](https://img.shields.io/badge/platform-linux--64%20%7C%20win--64-lightgrey?style=flat-square&logo=appveyor)]() [![python](https://img.shields.io/badge/python-3.X-blue?style=flat-square&logo=appveyor)](https://www.python.org/) [![license](https://img.shields.io/badge/license-GPL-green?style=flat-square&logo=appveyor)](https://www.gnu.org/licenses/gpl-3.0.en.html)




## Testing
TBD

## Status
> :construction: **MAPIT IS IN BETA** :construction: \
> \
> You may notice various bugs and errors. Help contribute to this project by reporting them through our issue page.

## Getting Started



MAPIT is primarily a GUI-based tool so launching the program is as simple as running ``MAPIT_main.py``. To get started, it is suggested that users try to use the included dataset to gain some familiarity with the tool. To do this, select the ``SNL curated dataset`` option when MAPIT starts and prompts for a dataset to be analyzed.




The ``SNL curated dataset`` allows users to explore the underlying process model used to generate the included example dataset that is based on IAEA-STR150 ([4](https://inis.iaea.org/search/search.aspx?orig_q=RN:17037216)). After loading the data (see below) the general workflow involves analysis of the loaded dataset.

![Scenario selection menu](assets/screenshots/SceneSelect2.png?raw=false "Scenario selection menu")

A general workflow is as follows:

* Designate statistical tests of interest using the checkboxes
* Specify material balance period and number of iterations
* (Optional) specify element in array of interest if importing own data
* Select errors
* Run and perform analysis
  * Note that all results can be exported for secondary analysis


## Documentation
* [User Guide](https://sandialabs.github.io/MAPIT/)
* [References - WIP]()


## Contact

* Nathan Shoman, Sandia National Laboratories, nshoman@sandia.gov

## Data Privacy

## License

* [License](LICENSE)
* [Third-Party Notice](NOTICE.md)

Sandia National Laboratories is a multimission laboratory managed and operated by National Technology and Engineering Solutions of Sandia, LLC, a wholly owned subsidiary of Honeywell International, Inc., for the U.S. Department of Energy's National Nuclear Security Administration under contract DE-NA-0003525.
