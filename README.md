# EVERSE-landscape

This repository serves to evaluate the outcomes of the landscaping survey from WP2 of the EVERSE project.

You can find the outcome of the survey in the *data* folder and generate a documentation of the survey outcomes by using the notebooks provided in *notebooks*.

## Contents
* **data** contains the survey results, data annotation and steering file to produce a report
* **src** contains supplementary functions
* **notebooks** contains the Jupyter notebooks to evaluate the survey

## Getting started

All survey responses are read and assigned an ID. Reading of the data is handled in the *DataSet* class, creating a plot with the *ReportMaker* class.

### Creating a report

See the notebook "Overview.ipynb" for an overview report of the survey. The structure of the survey is defined in the /data/structure.yml file. Here, each "cluster" of questions is displayed as a table, and a title and description for each chapter and table can be allocated.

## Open Questions

### Planned additional functionalities

- [ ] Adding display options for ratings and selection questions
- [ ] Weighting according to confidence questions
- [ ] Filtering of the dataset according to selection options (e.g. science cluster, representative view, ...)
- [ ] Documentation on use

### Display options

How should the result of the survey be displayed? Git pages? Pdf? ...?
--> Proposal to make the outcomes available as e.g. webpage and reference full report in the deliverable, using only highlight excerpts for report.

Any other additional requests?