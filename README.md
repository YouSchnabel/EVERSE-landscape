# EVERSE-landscape

This repository serves to evaluate the outcomes of the landscaping survey from WP2 of the EVERSE project.

You can find the outcome of the survey in the *data* folder and generate a documentation of the survey outcomes by using the notebooks provided in *notebooks*.

## Contents
* **data** contains the survey results, data annotation and steering file to produce a report
* **docs** contains the pages output and documentation
* **notebooks** contains the Jupyter notebooks to evaluate the survey
* **src** contains supplementary functions

## Getting started

All survey responses are read and assigned an ID. Reading of the data is handled in the *DataSet* class, creating a plot with the *ReportMaker* class.

### Creating a report

See the notebook "Overview.ipynb" for an overview report of the survey. The structure of the survey is defined in the /data/structure.yml file. Here, each "cluster" of questions is displayed as a table, and a title and description for each chapter and table can be allocated.

## Open Questions

### Planned additional functionalities

- [ ] Adding display options for all types of questions
    - [ ] References
    - [ ] Choice
    - [ ] Selection
    - [ ] Rating
    - [ ] Ranking
- [x] Output as markdown pages and deploy as pages
- [ ] Weighting according to confidence questions
- [ ] Filtering of the dataset according to selection options
    - [ ] Research clusters
    - [ ] Involvement
    - [ ] viewpoint
- [ ] Documentation on use (README and description)
