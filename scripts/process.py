# encoding: UTF-8

from __future__ import print_function

import os

import pandas as pd

path = os.path.dirname(os.path.realpath(__file__))
treaty_collection_url = ("https://treaties.un.org/Pages/" +
                         "showDetails.aspx?objid=0800000280458f37")
tabula_csv = os.path.join(path, "../archive/tabula-table.csv")
outfile = os.path.join(path, "../data/paris-agreement-entry-into-force.csv")

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
country_codes.loc["Czechia"] = "CZE"


# Ratification and Signature status from the UN treaty collection.
tables = pd.read_html(treaty_collection_url, encoding="UTF-8")

status = tables[5]
status.columns = status.loc[0]
status = status.reindex(status.index.drop(0))

status.index = status.Participant
status = status.drop("Participant", axis=1)
status.head()


signature = status.loc[status.Action == "Signature"]
signature = signature.rename(columns={
    "Date of Notification/Deposit": "Signature"
})
signature = pd.DataFrame(signature.Signature)

ratification = status.loc[status.Action != "Signature"]
ratification = ratification.rename(columns={
    "Action": "Kind",
    "Date of Notification/Deposit": "Ratification-Acceptance-Approval",
    "Date of Effect": "Date-Of-Effect"
    })

status = ratification.join(signature, how="outer")
status.index.name = "official_name_en"
status.index = status.index.str.replace("St\.", "Saint")

status = status[["Signature", "Ratification-Acceptance-Approval", "Kind"]]
status.Signature = pd.to_datetime(status.Signature, dayfirst=True)
status["Ratification-Acceptance-Approval"] = pd.to_datetime(
    status["Ratification-Acceptance-Approval"], dayfirst=True)


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

# Rename Czechia
status.index = status.index.str.replace(
    "Czech Republic", "Czechia")
emissions.index = emissions.index.str.replace(
    "Czech Republic", "Czechia")

emissions.index.name = "official_name_en"

# Listed in the footnotes of the table for the purpose of Article 21.
emissions.set_value("European Union", "Emissions", 4488404)
emissions.set_value("European Union", "Percentage", 12.10)
emissions.set_value("European Union", "Year", 2013)


export = status.join(emissions, how="outer").join(country_codes)
export = export.reset_index().set_index("country_code")
export = export.sort_values(by="official_name_en")

export.index.name = "Code"
export = export.rename(columns={
  "official_name_en": "Name"
})
print("\nData summary:\n")
print("Emissions sum w/o EU28: {:d} GgCO₂-equiv.".format(int(
    export.Emissions.sum() - export.Emissions.loc['EU28'].sum())))
print("Percentage sum: {}".format(
    export.Percentage.sum() - export.loc['EU28'].Percentage))
print("Count signatures: {}".format(export.Signature.count()))
print("Count ratified: {}".format(
    export["Ratification-Acceptance-Approval"].count()))
ratified = export["Ratification-Acceptance-Approval"].notnull()
percentage_sum = (export[ratified].Percentage.sum() -
                  export.loc["EU28"].Percentage)
print("Sum of percentages with ratification w/o EU28: {}".format(
    percentage_sum))


def to_int(x):
    if pd.isnull(x):
        return ""
    else:
        return str(int(x))


export.Emissions = export.Emissions.apply(to_int)
export.Year = export.Year.apply(to_int)
export.to_csv(outfile, encoding="UTF-8")
