[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/YouSchnabel/EVERSE-landscape/HEAD)
[![Pages](https://img.shields.io/badge/GitHub-Pages-blue.svg)](https://youschnabel.github.io/EVERSE-landscape/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# EVERSE-landscape

This repository serves to evaluate the outcomes of the landscaping survey from WP2 of the EVERSE project. The survey is available at [https://ec.europa.eu/eusurvey/runner/EVERSElandscaping](https://ec.europa.eu/eusurvey/runner/EVERSElandscaping).

You can find the outcome of the survey in the *data* folder and the generated report at the pages. You can recreate and adapt the report by using the notebooks provided in *notebooks*.

## Contents
* **data** contains the survey results, data annotation and steering file to produce a report
* **docs** contains the pages output and documentation
* **notebooks** contains the Jupyter notebooks to evaluate the survey
* **surveyer** contains supplementary functions

## Getting started

Some supplementary python classes are available and installable via pip. After cloning the repository, run
```
pip install .
```
to make the classes available. You can then execute the provided notebooks. An easy way to run it without downloading is by using binder, see link above. 

### Creating a report

All survey responses are read and assigned an ID. Reading of the data is handled in the *DataSet* class, creating a plot with the *ReportMaker* class. To generate a report, a configuration file is provided to the ReportMaker, which can be found in *data/structure.yml* and steers the display of the information.

See the notebook "Creating report.ipynb" for an overview report of the survey. For the creation of the configuration file, see the documentation.

## Open Questions

### Planned additional functionalities

- [x] Adding display options for all types of questions
    - [x] References
    - [x] Selection
    - [x] Rating
- [x] Output as markdown pages and deploy as pages
- [ ] Weighting according to confidence questions
- [ ] Filtering of the dataset according to selection options
    - [ ] Research clusters
    - [ ] Involvement
    - [ ] viewpoint
- [x] Install, mybinder, authors, metadata
- [x] Documentation on use (README and description)

