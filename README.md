Combined dataset of signature, ratification, acceptance or approval status
of the Paris Climate Agreement, and the emissions and shares for entry
into force for the purposes of Article 21 of the agreement.


## Data

Country codes are taken from the
[Country Codes data package](https://github.com/datasets/country-codes).

Signature, and ratification, acceptance or approval status is taken from the
[United Nations Treaty Collection](https://treaties.un.org/pages/ViewDetails.aspx?src=TREATY&mtdsg_no=XXVII-7-d&chapter=27&lang=en).

"[T]he most up-to-date total and per cent of
greenhouse gas emissions communicated by Parties to the Convention in their
national communications, greenhouse gas inventory reports, biennial reports or
biennial update reports, as of 12 December 2015", are extracted from the [PDF
file](http://unfccc.int/files/paris_agreement/application/pdf/10e.pdf) on the
[UNFCCC Paris Agreement - Status of Ratification](http://unfccc.int/paris_agreement/items/9444.php) page.


## Preparation

Install requirements:

```shell
pip install -r scripts/requirements.txt
```

Get PDF with emissions data:

```shell
make emissions-table
```

The table  needs to be manually extracted into a file
`archive/tabula-table.csv` using [Tabula](http://tabula.technology/).

To process the data the current signature and ratification status is downloaded
before generating the combined CSV file:

```shell
make
```

To update the dataset only the last step needs to be run.


## Notes

Due to rounding the sums of emissions and percentage shares differ from the ones
reported in the summary in the PDF table with reported emissions for the
purpose of Article 21 of the agreement.
