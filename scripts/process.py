# encoding: UTF-8

from __future__ import print_function

import os

import pandas as pd

from lxml import etree
from StringIO import StringIO

path = os.path.dirname(os.path.realpath(__file__))
treaty_collection = os.path.join(path, "../archive/treaty-collection.html")
tabula_csv = os.path.join(path, "../archive/tabula-table.csv")
outfile = os.path.join(path, "../data/paris-agreement-entry-into-force.csv")

parser = etree.HTMLParser()

# Country codes
url = ("https://raw.githubusercontent.com/" +
       "datasets/country-codes/master/data/country-codes.csv")

country_codes = pd.read_csv(
    url,
    index_col="official_name_en",
    usecols=["ISO3166-1-Alpha-3", "official_name_en"],
    encoding="UTF-8"
)
country_codes = country_codes.rename(
    columns={"ISO3166-1-Alpha-3": "country_code"}
)

# Add country code for European Union
country_codes.loc["European Union"] = 'EU28'

# Status in treaty collection.
with open(treaty_collection, "rb") as f:
    html = f.read()

tree = etree.parse(StringIO(html), parser)

selector = ('//table[@id="ctl00_ctl00_ContentPlaceHolder1' +
            '_ContentPlaceHolderInnerPage_tblgrid"]')
table = etree.tostring(tree.xpath(selector)[0])


def dateparse(x):
    if pd.isnull(x):
        return x
    else:
        return pd.datetime.strptime(x, '%d %b %Y').date()


status = pd.read_html(table, index_col=0, header=0)[0]

status.iloc[:, 0] = status.iloc[:, 0].apply(dateparse)
status.iloc[:, 1] = status.iloc[:, 1].apply(dateparse)

status.index = status.index.str.replace("St\.", "Saint")
status.index.name = "official_name_en"

status = status.rename(columns={
    "Signature": "signature",
    "Ratification, Acceptance(A), Approval(AA)":
        "ratification_acceptance_approval"
})

# Emissions and shares for each country.
# The tabula-table.csv file was generated using Tabula
# (http://tabula.technology/).


def make_int(field):
    try:
        return int(field.replace(" ", ""))
    except ValueError:
        if field == "n/a" or "n/a ":
            return pd.np.NaN
        else:
            return field


# Header rows have been split: "Emissions Gg CO₂ equivalent""
emissions = pd.read_csv(
    "archive/tabula-table.csv",
    index_col=0,
    na_values=["n/a ", "n/a"],
    skiprows=0,
    header=1,
    converters={u'equivalent) ': make_int}
)
emissions.columns = [c.strip() for c in emissions.columns]
emissions.index = [c.strip() for c in emissions.index]
emissions.index.names = ['Party']
emissions = emissions.rename(columns={"equivalent)": "Emissions"})

# Fix country names that were printed on two lines.
emissions = emissions.rename(index={
    "Bolivia (Plurinational State": "Bolivia (Plurinational State of)",
    "Democratic People's Republic": "Democratic People's Republic of Korea",
    "Democratic Republic of the": "Democratic Republic of the Congo",
    "Lao People's Democratic": "Lao People's Democratic Republic",
    "Micronesia (Federated States": "Micronesia (Federated States of)",
    "Saint Vincent and the": "Saint Vincent and the Grenadines",
    "The former Yugoslav": "The former Yugoslav Republic of Macedonia",
    "United Kingdom of Great":
        "United Kingdom of Great Britain and Northern Ireland",
    "Venezuela (Bolivarian": "Venezuela (Bolivarian Republic of)"
})
emissions = emissions.drop([
    "of)",
    "of Korea",
    "Republic",
    "Grenadines",
    "Republic of Macedonia",
    "Britain and Northern Ireland*",
    "Republic of)"
])
# Drop empty remaining Congo column of "Democratic Republic of the Congo".
emissions = emissions[~emissions.index.duplicated()]

emissions.index = emissions.index.str.replace(
    "Cote d'Ivoire", u"Côte d'Ivoire")

rename_eu_countries = {i: i[:-1] for i in emissions.index if i.endswith("*")}
assert(len(rename_eu_countries) == 27)  # UK already fixed above.
emissions = emissions.rename(index=rename_eu_countries)

emissions = emissions.drop("Total")

emissions.index.name = "official_name_en"
emissions.columns = [c.lower() for c in emissions.columns]

# Listed in the footnotes of the table for the purpose of Article 21.
emissions.set_value("European Union", "emissions", 4488404)
emissions.set_value("European Union", "percentage", 12.10)
emissions.set_value("European Union", "year", 2013)

export = status.join(emissions, how="outer").join(country_codes)
export = export.reset_index().set_index("country_code")
export = export.sort_values(by="official_name_en")

print("\nData summary:\n")
print("Emissions sum w/o EU28: {:d} GgCO₂-equiv.".format(int(
    export.emissions.sum() - export.emissions.loc['EU28'].sum())))
print("Percentage sum: {}".format(
    export.percentage.sum() - export.loc['EU28'].percentage))
print("Count signatures: {}".format(export.signature.count()))
print("Count ratified: {}".format(
    export.ratification_acceptance_approval.count()))
ratified = export.ratification_acceptance_approval.notnull()
percentage_sum = export[ratified].percentage.sum()
print("Sum of percentages with ratification: {}".format(percentage_sum))


def to_int(x):
    if pd.isnull(x):
        return ""
    else:
        return str(int(x))


export.emissions = export.emissions.apply(to_int)
export.year = export.year.apply(to_int)
export.to_csv(outfile, encoding="UTF-8")
