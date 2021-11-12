Combined dataset of signature, ratification, acceptance or approval status
of the Paris Climate Agreement, and the emissions and shares for entry
into force for the purposes of Article 21 of the agreement.

[![Daily Update](https://github.com/openclimatedata/paris-agreement-entry-into-force/workflows/Update%20data/badge.svg)](https://github.com/openclimatedata/paris-agreement-entry-into-force/actions)

## Data

Signature, and ratification, acceptance or approval status is taken from the
[United Nations Treaty Collection](https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=XXVII-7-d&chapter=27&clang=_en) by parsing the [full record page](https://treaties.un.org/Pages/showDetails.aspx?objid=0800000280458f37).

"[T]he most up-to-date total and per cent of
greenhouse gas emissions communicated by Parties to the Convention in their
national communications, greenhouse gas inventory reports, biennial reports or
biennial update reports, as of 12 December 2015", are extracted from the [PDF
file](http://unfccc.int/files/paris_agreement/application/pdf/10e.pdf) on the
[UNFCCC Paris Agreement - Status of Ratification](http://unfccc.int/paris_agreement/items/9444.php) page.


## Preparation

There are daily checks for updates, to update manually see below.

The `Makefile` requires Python3 and will automatically install its dependencies
into a Virtualenv when run with

```shell
make
```
This will also fetch the latest data and print a diff of any changed data.


To get the PDF with emissions data (already included in the Data Package):

```shell
make emissions-table
```

The table  needs to be manually extracted into a file
`archive/tabula-table.csv` using [Tabula](http://tabula.technology/).


## Notes

Due to rounding the sums of emissions and percentage shares differ from the ones
reported in the summary in the PDF table with reported emissions for the
purpose of Article 21 of the agreement.
